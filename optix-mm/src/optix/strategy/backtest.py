"""Historical backtester for OptimismTax-MM.

Replays Becker's trades chronologically. Whenever a YES-buying taker hits
the tape on a qualifying market at a longshot price, we model the strategy
as if it had a resting NO bid one tick below the trade's NO price. We
treat the strategy's fill probability as 1.0 for paper-simplicity (in
live trading the rate will be lower).

Outputs:
    runs/backtest-{stamp}.json
    runs/backtest-{stamp}-equity.png
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import polars as pl

from optix.config import get_settings
from optix.data.becker_loader import BeckerDataPaths, connect, trades_with_outcomes
from optix.data.categories import category_for_event_ticker
from optix.research.calibration import load_calibration, yes_winrate_for
from optix.research.jepa_forecaster.registry import ForecastRegistry
from optix.research.jepa_forecaster.runtime import ForecasterRuntime
from optix.strategy.signals import TradeTick, decide


@dataclass
class Position:
    market_ticker: str
    contracts: int = 0
    cost_cents: int = 0  # total cost basis across all fills, in cents
    realized_pnl_cents: int = 0


@dataclass
class BacktestResult:
    n_fills: int = 0
    n_markets_with_position: int = 0
    capital_deployed_usd: float = 0.0
    realized_pnl_usd: float = 0.0
    equity_curve: list[tuple[str, float]] = field(default_factory=list)
    per_category: dict[str, dict[str, float]] = field(default_factory=dict)
    forecast_mode: str = "structural_only"
    forecast_artifact_id: str = ""
    forecaster_loaded: bool = False


def run_backtest(start: str | None = None, end: str | None = None) -> BacktestResult:
    s = get_settings()
    paths = BeckerDataPaths.from_settings()
    con = connect()

    print(f"Loading trades (lookback={s.optix_taker_lookback_trades})...")
    trades = trades_with_outcomes(
        con,
        paths,
        price_lo=s.optix_longshot_price_lo_cents,
        price_hi=s.optix_longshot_price_hi_cents,
        min_market_volume=100,
    )
    if start:
        trades = trades.filter(pl.col("ts") >= datetime.fromisoformat(start))
    if end:
        trades = trades.filter(pl.col("ts") <= datetime.fromisoformat(end))

    trades = trades.sort("ts")
    print(f"Replaying {trades.height:,} trades")

    calibration = load_calibration()
    if not calibration:
        print("WARNING: no calibration table found. EV will be zero everywhere.")
        print("Run: uv run python -m optix.research.calibration")

    runtime: ForecasterRuntime | None = None
    forecaster_loaded = False
    if s.optix_forecast_mode != "structural_only" and s.optix_forecast_artifact_id:
        mp = ForecastRegistry().model_path(s.optix_forecast_artifact_id)
        if mp.exists():
            runtime = ForecasterRuntime.from_joblib(mp)
            forecaster_loaded = True
            print(f"Loaded forecaster artifact {s.optix_forecast_artifact_id}")
        else:
            print(
                "WARNING: optix_forecast_artifact_id set but model file missing; "
                "using calibration-only EV."
            )

    # Per-market state
    windows: dict[str, deque[TradeTick]] = defaultdict(
        lambda: deque(maxlen=s.optix_taker_lookback_trades)
    )
    positions: dict[str, Position] = {}
    market_results: dict[str, str] = {}
    market_categories: dict[str, str] = {}

    bankroll_usd = s.optix_bankroll_usd
    realized_pnl_usd = 0.0
    n_fills = 0
    equity_curve: list[tuple[str, float]] = []

    for row in trades.iter_rows(named=True):
        ticker = row["ticker"]
        category = market_categories.setdefault(
            ticker, category_for_event_ticker(row.get("event_ticker"))
        )
        market_results[ticker] = row["result"]

        tick = TradeTick(
            ts_ms=int(row["ts"].timestamp() * 1000),
            yes_price_cents=int(row["yes_price"]),
            taker_side=row["taker_side"],
            count=int(row["count"]),
        )
        win = windows[ticker]
        win.append(tick)

        # Get open position size
        pos = positions.setdefault(ticker, Position(market_ticker=ticker))

        # Run signal pipeline using the trade's prices as our reference
        forecast_p: float | None = None
        if runtime is not None:
            try:
                forecast_p = runtime.predict_p_yes_from_ticks(win, category)
            except Exception:
                forecast_p = None

        decision = decide(
            market_ticker=ticker,
            category=category,
            yes_price_cents=tick.yes_price_cents,
            no_price_cents=int(row["no_price"]),
            trade_window=win,
            historical_yes_winrate=yes_winrate_for(category, tick.yes_price_cents, calibration),
            bankroll_usd=bankroll_usd,
            open_position_contracts=pos.contracts,
            forecast_p_yes=forecast_p,
        )

        if decision.action == "POST_NO_BID" and tick.taker_side == "yes":
            # Model the resting NO bid as filling against this YES-taker order.
            # Conservative: cap our fill at the trade's count and at our requested size.
            fill_count = min(decision.size_contracts, tick.count)
            if fill_count <= 0:
                continue
            fill_price_cents = decision.target_no_price_cents or int(row["no_price"])
            pos.contracts += fill_count
            pos.cost_cents += fill_count * fill_price_cents
            n_fills += 1

    # Settle all positions at expiry
    realized_per_cat: dict[str, float] = defaultdict(float)
    capital_per_cat: dict[str, float] = defaultdict(float)
    for ticker, pos in positions.items():
        if pos.contracts == 0:
            continue
        result = market_results.get(ticker)
        category = market_categories.get(ticker, "Other")
        # NO contract pays $1 (=100c) when result == 'no'
        payout_cents = pos.contracts * 100 if result == "no" else 0
        pnl_cents = payout_cents - pos.cost_cents
        pos.realized_pnl_cents = pnl_cents
        pnl_usd = pnl_cents / 100.0
        realized_pnl_usd += pnl_usd
        realized_per_cat[category] += pnl_usd
        capital_per_cat[category] += pos.cost_cents / 100.0
        equity_curve.append((str(market_results.get(ticker)), realized_pnl_usd))

    n_markets_with_position = sum(1 for p in positions.values() if p.contracts > 0)
    capital_usd = sum(p.cost_cents for p in positions.values()) / 100.0

    per_category: dict[str, dict[str, float]] = {}
    for cat, pnl in realized_per_cat.items():
        cap = capital_per_cat[cat]
        per_category[cat] = {
            "capital_usd": round(cap, 2),
            "realized_pnl_usd": round(pnl, 2),
            "roi_pct": round(100.0 * pnl / cap, 3) if cap > 0 else 0.0,
        }

    return BacktestResult(
        n_fills=n_fills,
        n_markets_with_position=n_markets_with_position,
        capital_deployed_usd=round(capital_usd, 2),
        realized_pnl_usd=round(realized_pnl_usd, 2),
        equity_curve=equity_curve,
        per_category=per_category,
        forecast_mode=s.optix_forecast_mode,
        forecast_artifact_id=s.optix_forecast_artifact_id or "",
        forecaster_loaded=forecaster_loaded,
    )


def save_result(result: BacktestResult) -> Path:
    s = get_settings()
    stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    path = s.optix_log_dir / f"backtest-{stamp}.json"
    path.write_text(json.dumps({
        "n_fills": result.n_fills,
        "n_markets_with_position": result.n_markets_with_position,
        "capital_deployed_usd": result.capital_deployed_usd,
        "realized_pnl_usd": result.realized_pnl_usd,
        "forecast_mode": result.forecast_mode,
        "forecast_artifact_id": result.forecast_artifact_id,
        "forecaster_loaded": result.forecaster_loaded,
        "roi_pct": (
            100.0 * result.realized_pnl_usd / result.capital_deployed_usd
            if result.capital_deployed_usd > 0 else 0.0
        ),
        "per_category": result.per_category,
    }, indent=2))

    if result.equity_curve:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(range(len(result.equity_curve)), [pnl for _, pnl in result.equity_curve])
        ax.set_xlabel("Settled position #")
        ax.set_ylabel("Cumulative realized PnL ($)")
        ax.set_title("OptimismTax-MM backtest equity curve")
        ax.grid(True, alpha=0.3)
        png_path = s.optix_log_dir / f"backtest-{stamp}-equity.png"
        fig.savefig(png_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
    return path
