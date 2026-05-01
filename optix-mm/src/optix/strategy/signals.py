"""Signal computation for OptimismTax-MM.

The strategy is a structural-alpha capture, not a forecaster. It posts NO
liquidity on markets where (a) YES is at longshot prices, (b) the recent
trade tape is dominated by YES-buying takers, and (c) the market category
has a documented maker-taker gap.

All signals are pure functions over deque-shaped state to keep the live
runner stateless and testable.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from optix.config import get_settings
from optix.data.categories import CATEGORY_GAP_PP, is_target_category
from optix.research.jepa_forecaster.types import ForecastMode


@dataclass
class TradeTick:
    """Minimal projection of a Kalshi trade event."""
    ts_ms: int
    yes_price_cents: int
    taker_side: str  # 'yes' | 'no'
    count: int


@dataclass
class Decision:
    """Output of the signal pipeline. NO_TRADE if no qualifying setup."""
    market_ticker: str
    action: str  # 'POST_NO_BID' | 'CANCEL_ALL' | 'NO_TRADE'
    target_no_price_cents: int | None = None
    size_contracts: int = 0
    reason: str = ""


def taker_yes_imbalance(window: deque[TradeTick]) -> float:
    """Fraction of recent volume coming from YES-buying takers.

    Returns 0.5 for an empty window so we don't spuriously fire on no data.
    """
    if not window:
        return 0.5
    yes_vol = sum(t.count for t in window if t.taker_side == "yes")
    total = sum(t.count for t in window)
    return yes_vol / total if total > 0 else 0.5


def is_longshot_yes(yes_price_cents: int) -> bool:
    s = get_settings()
    return s.optix_longshot_price_lo_cents <= yes_price_cents <= s.optix_longshot_price_hi_cents


def effective_yes_winrate(
    historical_yes_winrate: float | None,
    forecast_p_yes: float | None,
    mode: ForecastMode,
    alpha: float,
) -> float | None:
    """Blend calibration table estimate with JEPA-Forecaster probability."""
    if mode == ForecastMode.STRUCTURAL_ONLY:
        return historical_yes_winrate
    if mode == ForecastMode.FORECAST_ABLATION:
        return forecast_p_yes if forecast_p_yes is not None else historical_yes_winrate
    # HYBRID
    if forecast_p_yes is None:
        return historical_yes_winrate
    if historical_yes_winrate is None:
        return forecast_p_yes
    a = max(0.0, min(1.0, alpha))
    return (1.0 - a) * historical_yes_winrate + a * forecast_p_yes


def expected_value_per_contract_cents(
    yes_price_cents: int,
    historical_yes_winrate: float | None = None,
) -> float:
    """Expected profit (in cents) of buying NO at the complementary price.

    If we have an empirical winrate from Becker's calibration, use it; else
    fall back to assuming the YES price is the true probability (zero-edge).

    Buying NO at q = 100 - p costs q cents. NO pays 100 if YES loses.
    EV per contract:
        win  with prob (1 - p_true): receive (100 - q) = p cents
        lose with prob p_true:       receive -q cents
    EV = (1 - p_true) * p - p_true * q
       = p - p_true * (p + q)
       = p - 100 * p_true             (since p + q = 100)
    """
    p = yes_price_cents
    if historical_yes_winrate is None:
        # Assume calibrated. EV = p - 100*(p/100) = 0. Used only as a stub.
        return 0.0
    return p - 100.0 * historical_yes_winrate


def decide(
    market_ticker: str,
    category: str,
    yes_price_cents: int,
    no_price_cents: int,
    trade_window: deque[TradeTick],
    historical_yes_winrate: float | None,
    bankroll_usd: float,
    open_position_contracts: int,
    forecast_p_yes: float | None = None,
) -> Decision:
    """Top-level signal pipeline.

    Logic:
      1. Skip non-target categories (esp. Finance: gap is 0.17pp, not worth it).
      2. Skip if YES is not in longshot regime.
      3. Skip if recent flow isn't YES-skewed enough.
      4. Skip if expected edge per contract is non-positive.
      5. Otherwise, compute size and post a NO bid one tick below the
         current best NO offer.
    """
    s = get_settings()
    targets = s.target_category_set
    mode = ForecastMode(s.optix_forecast_mode)

    if not is_target_category(category, targets):
        return Decision(market_ticker, "NO_TRADE", reason=f"category {category} not in targets")

    if not is_longshot_yes(yes_price_cents):
        return Decision(market_ticker, "NO_TRADE", reason=f"YES {yes_price_cents}c not longshot")

    imbalance = taker_yes_imbalance(trade_window)
    if imbalance < s.optix_taker_imbalance_threshold:
        return Decision(
            market_ticker, "NO_TRADE",
            reason=f"taker YES imbalance {imbalance:.2f} < {s.optix_taker_imbalance_threshold}",
        )

    blended = effective_yes_winrate(
        historical_yes_winrate,
        forecast_p_yes,
        mode,
        s.optix_forecast_hybrid_alpha,
    )
    ev_cents = expected_value_per_contract_cents(yes_price_cents, blended)
    if ev_cents <= 0:
        return Decision(
            market_ticker, "NO_TRADE",
            reason=f"EV {ev_cents:.2f}c not positive",
        )

    # Cap exposure per market
    max_capital_cents = bankroll_usd * 100 * (s.optix_per_market_cap_pct / 100.0)
    cost_per_contract_cents = no_price_cents
    max_contracts = int(max_capital_cents // max(cost_per_contract_cents, 1))
    available = max(0, max_contracts - open_position_contracts)
    if available <= 0:
        return Decision(
            market_ticker, "NO_TRADE",
            reason=f"position cap reached ({open_position_contracts} contracts)",
        )

    # Size proportional to documented category gap (more aggressive in higher-gap cats)
    gap_pp = CATEGORY_GAP_PP.get(category, 1.0)
    size_factor = min(1.0, gap_pp / 5.0)  # 5pp gap or higher -> full size
    size = max(1, int(available * size_factor))

    # Post one tick below the best ask (i.e., at no_price - 1) to be passive
    target_no = max(1, no_price_cents - 1)

    return Decision(
        market_ticker=market_ticker,
        action="POST_NO_BID",
        target_no_price_cents=target_no,
        size_contracts=size,
        reason=(
            f"YES={yes_price_cents}c imbalance={imbalance:.2f} "
            f"gap={gap_pp:.2f}pp ev={ev_cents:+.2f}c size={size} "
            f"mode={mode.value}"
        ),
    )
