"""Unit tests for the signal pipeline and risk manager.

Run with:
    uv run pytest -v
"""

from collections import deque

import pytest

from optix.config import get_settings
from optix.risk.limits import RiskManager
from optix.strategy.signals import (
    TradeTick,
    decide,
    expected_value_per_contract_cents,
    is_longshot_yes,
    taker_yes_imbalance,
)


def make_window(taker_sides: list[str], count_each: int = 1) -> deque[TradeTick]:
    return deque(
        TradeTick(ts_ms=i, yes_price_cents=5, taker_side=s, count=count_each)
        for i, s in enumerate(taker_sides)
    )


# ---------------- helpers ----------------


def test_taker_yes_imbalance_empty_returns_half():
    assert taker_yes_imbalance(deque()) == 0.5


def test_taker_yes_imbalance_pure_yes():
    win = make_window(["yes"] * 10)
    assert taker_yes_imbalance(win) == 1.0


def test_taker_yes_imbalance_pure_no():
    win = make_window(["no"] * 10)
    assert taker_yes_imbalance(win) == 0.0


def test_taker_yes_imbalance_mixed():
    win = make_window(["yes", "yes", "yes", "no"])
    assert taker_yes_imbalance(win) == pytest.approx(0.75)


def test_is_longshot_yes_inside_band():
    assert is_longshot_yes(5)
    assert is_longshot_yes(15)
    assert is_longshot_yes(1)


def test_is_longshot_yes_outside_band():
    assert not is_longshot_yes(20)
    assert not is_longshot_yes(50)
    assert not is_longshot_yes(0)


def test_ev_zero_when_calibrated():
    # If true winrate equals implied probability, EV is zero.
    assert expected_value_per_contract_cents(5, historical_yes_winrate=0.05) == pytest.approx(0)


def test_ev_positive_when_yes_overpriced():
    # YES at 5c but really only wins 3% -> NO is +2c per contract
    assert expected_value_per_contract_cents(5, historical_yes_winrate=0.03) == pytest.approx(2.0)


# ---------------- decide() ----------------


def test_decide_skips_finance():
    win = make_window(["yes"] * 10)
    d = decide(
        market_ticker="X",
        category="Finance",
        yes_price_cents=5,
        no_price_cents=95,
        trade_window=win,
        historical_yes_winrate=0.03,
        bankroll_usd=10_000,
        open_position_contracts=0,
    )
    assert d.action == "NO_TRADE"
    assert "Finance" in d.reason or "category" in d.reason


def test_decide_skips_when_yes_not_longshot():
    win = make_window(["yes"] * 10)
    d = decide(
        market_ticker="X",
        category="Sports",
        yes_price_cents=50,
        no_price_cents=50,
        trade_window=win,
        historical_yes_winrate=0.45,
        bankroll_usd=10_000,
        open_position_contracts=0,
    )
    assert d.action == "NO_TRADE"


def test_decide_skips_when_imbalance_too_low():
    win = make_window(["yes", "no", "yes", "no", "yes", "no"])  # 50/50
    d = decide(
        market_ticker="X",
        category="Sports",
        yes_price_cents=5,
        no_price_cents=95,
        trade_window=win,
        historical_yes_winrate=0.03,
        bankroll_usd=10_000,
        open_position_contracts=0,
    )
    assert d.action == "NO_TRADE"
    assert "imbalance" in d.reason


def test_decide_skips_when_ev_non_positive():
    win = make_window(["yes"] * 10)
    d = decide(
        market_ticker="X",
        category="Sports",
        yes_price_cents=5,
        no_price_cents=95,
        trade_window=win,
        historical_yes_winrate=0.10,  # YES wins 10% but only priced 5c -> NO is bad bet
        bankroll_usd=10_000,
        open_position_contracts=0,
    )
    assert d.action == "NO_TRADE"
    assert "EV" in d.reason


def test_decide_posts_no_bid_when_all_signals_align():
    win = make_window(["yes"] * 10)
    d = decide(
        market_ticker="NFLGAME-X",
        category="Sports",
        yes_price_cents=5,
        no_price_cents=95,
        trade_window=win,
        historical_yes_winrate=0.03,
        bankroll_usd=10_000,
        open_position_contracts=0,
    )
    assert d.action == "POST_NO_BID"
    assert d.target_no_price_cents == 94  # one tick below best ask
    assert d.size_contracts > 0


def test_decide_respects_position_cap():
    """If we're already at our position cap, no further bids."""
    s = get_settings()
    win = make_window(["yes"] * 10)
    # Per-market cap 1% of $10k = $100 = 10000c. At 95c per NO contract that's ~105 contracts.
    cap_contracts = int(10_000 * 100 * (s.optix_per_market_cap_pct / 100.0) / 95)
    d = decide(
        market_ticker="X",
        category="Sports",
        yes_price_cents=5,
        no_price_cents=95,
        trade_window=win,
        historical_yes_winrate=0.03,
        bankroll_usd=10_000,
        open_position_contracts=cap_contracts,
    )
    assert d.action == "NO_TRADE"
    assert "cap" in d.reason


# ---------------- risk ----------------


def test_risk_manager_starts_un_halted():
    rm = RiskManager(bankroll_usd=10_000)
    assert rm.can_trade()
    assert rm.snapshot()["halted"] is False


def test_risk_manager_halts_on_daily_dd():
    rm = RiskManager(bankroll_usd=10_000)
    # 4% halt = $400 loss
    rm.record_realized(-200)
    assert rm.can_trade()
    rm.record_realized(-201)
    assert not rm.can_trade()


def test_risk_manager_per_market_cap():
    rm = RiskManager(bankroll_usd=10_000)
    assert rm.per_market_cap_usd() == pytest.approx(100.0)
