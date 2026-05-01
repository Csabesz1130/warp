"""Risk manager: position caps, daily drawdown, kill switch.

The single most important file in a trading system. Everything else can
have bugs and you'll just lose less alpha. A bug here loses your bankroll.
Keep the logic dumb-simple and test it before anything else.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from optix.config import get_settings


@dataclass
class RiskState:
    bankroll_usd: float
    starting_equity_today: float
    realized_pnl_today: float = 0.0
    halted: bool = False
    halt_reason: str = ""
    today: date = field(default_factory=lambda: datetime.now(timezone.utc).date())


class RiskManager:
    def __init__(self, bankroll_usd: float | None = None) -> None:
        s = get_settings()
        bk = bankroll_usd or s.optix_bankroll_usd
        self.state = RiskState(bankroll_usd=bk, starting_equity_today=bk)
        self._dd_halt_pct = s.optix_daily_dd_halt_pct
        self._per_market_cap_pct = s.optix_per_market_cap_pct

    def per_market_cap_usd(self) -> float:
        return self.state.bankroll_usd * (self._per_market_cap_pct / 100.0)

    def daily_dd_threshold_usd(self) -> float:
        return self.state.starting_equity_today * (self._dd_halt_pct / 100.0)

    def record_realized(self, pnl_usd: float) -> None:
        self.state.realized_pnl_today += pnl_usd
        self.state.bankroll_usd += pnl_usd
        self._roll_day_if_needed()
        self._check_halt()

    def can_trade(self) -> bool:
        self._roll_day_if_needed()
        return not self.state.halted

    def reset_halt(self) -> None:
        self.state.halted = False
        self.state.halt_reason = ""

    def _check_halt(self) -> None:
        if self.state.halted:
            return
        if -self.state.realized_pnl_today >= self.daily_dd_threshold_usd():
            self.state.halted = True
            self.state.halt_reason = (
                f"daily DD halt: {self.state.realized_pnl_today:+.2f} <= "
                f"-{self.daily_dd_threshold_usd():.2f}"
            )

    def _roll_day_if_needed(self) -> None:
        today = datetime.now(timezone.utc).date()
        if today != self.state.today:
            self.state.today = today
            self.state.realized_pnl_today = 0.0
            self.state.starting_equity_today = self.state.bankroll_usd
            self.state.halted = False
            self.state.halt_reason = ""

    def snapshot(self) -> dict[str, float | bool | str]:
        return {
            "bankroll_usd": round(self.state.bankroll_usd, 2),
            "starting_equity_today": round(self.state.starting_equity_today, 2),
            "realized_pnl_today": round(self.state.realized_pnl_today, 2),
            "per_market_cap_usd": round(self.per_market_cap_usd(), 2),
            "daily_dd_threshold_usd": round(self.daily_dd_threshold_usd(), 2),
            "halted": self.state.halted,
            "halt_reason": self.state.halt_reason,
        }
