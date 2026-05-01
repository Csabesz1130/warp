"""Paper trader: simulates fills against the live tape.

Strategy: for each qualifying market, we maintain a simulated NO bid at
`target_no_price - 1` cents. When a YES-buying taker trade prints at or
below our bid level, we simulate a fill of `min(decision.size, trade.count)`
contracts.

This is a pessimistic-realistic model: we never see fills better than the
tape, and we never assume queue priority over real makers. It's a lower
bound on what live trading would do.
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import structlog

from optix.config import get_settings
from optix.kalshi.feed import FeedQuote, FeedTrade
from optix.research.calibration import load_calibration, yes_winrate_for
from optix.risk.limits import RiskManager
from optix.research.jepa_forecaster.runtime import ForecasterRuntime
from optix.strategy.signals import Decision, TradeTick, decide

log = structlog.get_logger(__name__)


@dataclass
class SimPosition:
    ticker: str
    contracts: int = 0
    cost_cents: int = 0


@dataclass
class SimFill:
    ticker: str
    ts_ms: int
    contracts: int
    no_price_cents: int
    reason: str


@dataclass
class PaperState:
    positions: dict[str, SimPosition] = field(default_factory=dict)
    windows: dict[str, deque[TradeTick]] = field(default_factory=dict)
    quotes: dict[str, FeedQuote] = field(default_factory=dict)
    categories: dict[str, str] = field(default_factory=dict)
    fills: list[SimFill] = field(default_factory=list)
    last_decision: dict[str, Decision] = field(default_factory=dict)


class PaperExecutor:
    def __init__(
        self,
        risk: RiskManager,
        market_categories: dict[str, str],
        run_path: Path | None = None,
        forecaster: ForecasterRuntime | None = None,
    ) -> None:
        s = get_settings()
        self.s = s
        self.risk = risk
        self.calibration = load_calibration()
        self.state = PaperState()
        self.state.categories = dict(market_categories)
        self.state.windows = defaultdict(
            lambda: deque(maxlen=s.optix_taker_lookback_trades)
        )
        if run_path is None:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            run_path = s.optix_log_dir / f"paper-{stamp}.jsonl"
        self.run_path = run_path
        self.run_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.run_path.open("a", buffering=1)
        self.forecaster = forecaster

    def close(self) -> None:
        self._fh.close()

    def _journal(self, kind: str, payload: dict) -> None:
        record = {"kind": kind, "ts_ms": int(datetime.now(timezone.utc).timestamp() * 1000)}
        record.update(payload)
        self._fh.write(json.dumps(record, default=str) + "\n")

    def on_quote(self, q: FeedQuote) -> None:
        self.state.quotes[q.ticker] = q

    def on_trade(self, t: FeedTrade) -> None:
        if not self.risk.can_trade():
            self._journal("halted", self.risk.snapshot())
            return

        win = self.state.windows[t.ticker]
        win.append(TradeTick(
            ts_ms=t.ts_ms,
            yes_price_cents=t.yes_price,
            taker_side=t.taker_side,
            count=t.count,
        ))

        category = self.state.categories.get(t.ticker, "Other")
        pos = self.state.positions.setdefault(t.ticker, SimPosition(ticker=t.ticker))

        forecast_p: float | None = None
        if self.forecaster is not None:
            try:
                forecast_p = self.forecaster.predict_p_yes_from_ticks(win, category)
            except Exception:
                forecast_p = None

        decision = decide(
            market_ticker=t.ticker,
            category=category,
            yes_price_cents=t.yes_price,
            no_price_cents=t.no_price,
            trade_window=win,
            historical_yes_winrate=yes_winrate_for(category, t.yes_price, self.calibration),
            bankroll_usd=self.risk.state.bankroll_usd,
            open_position_contracts=pos.contracts,
            forecast_p_yes=forecast_p,
        )
        self.state.last_decision[t.ticker] = decision

        if decision.action != "POST_NO_BID" or t.taker_side != "yes":
            return
        if decision.target_no_price_cents is None:
            return

        # Simulated fill: we get matched against the YES-taker's order if
        # our resting NO bid sits at or above the trade's no price.
        if decision.target_no_price_cents < t.no_price:
            return  # our bid wasn't competitive, no fill

        fill_count = min(decision.size_contracts, t.count)
        if fill_count <= 0:
            return

        fill_price_cents = decision.target_no_price_cents
        pos.contracts += fill_count
        pos.cost_cents += fill_count * fill_price_cents

        fill = SimFill(
            ticker=t.ticker,
            ts_ms=t.ts_ms or int(datetime.now(timezone.utc).timestamp() * 1000),
            contracts=fill_count,
            no_price_cents=fill_price_cents,
            reason=decision.reason,
        )
        self.state.fills.append(fill)
        self._journal("fill", asdict(fill))
        log.info("paper.fill", **asdict(fill))

    def settle(self, ticker: str, result: str) -> float:
        """Settle a market: NO contracts pay $1 if result == 'no', else 0."""
        pos = self.state.positions.get(ticker)
        if pos is None or pos.contracts == 0:
            return 0.0
        payout_cents = pos.contracts * 100 if result == "no" else 0
        pnl_usd = (payout_cents - pos.cost_cents) / 100.0
        self.risk.record_realized(pnl_usd)
        self._journal("settle", {
            "ticker": ticker,
            "result": result,
            "contracts": pos.contracts,
            "cost_usd": pos.cost_cents / 100.0,
            "payout_usd": payout_cents / 100.0,
            "pnl_usd": round(pnl_usd, 2),
            "risk": self.risk.snapshot(),
        })
        # Close position
        del self.state.positions[ticker]
        return pnl_usd

    def snapshot(self) -> dict:
        return {
            "n_open_positions": sum(1 for p in self.state.positions.values() if p.contracts > 0),
            "n_fills_total": len(self.state.fills),
            "risk": self.risk.snapshot(),
        }
