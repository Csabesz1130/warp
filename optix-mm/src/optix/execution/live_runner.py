"""Top-level live runner. Connects feed, decides, paper-executes, settles.

Usage:
    uv run python scripts/run_paper.py [--max-markets N]

What it does:
  1. Calls list_markets to get all open markets in our target categories.
  2. Subscribes to trade + orderbook_delta channels for those tickers.
  3. Streams events, runs the signal pipeline, journals decisions.
  4. Polls the REST API every 60s for newly-resolved markets and settles
     paper positions to realized PnL.

Live order placement is intentionally NOT implemented in this file. To go
live you must add an order-placement method to KalshiREST, replace the
`paper.on_trade` call with an order-router call, and double-check every
risk gate. Don't shortcut this.
"""

from __future__ import annotations

import asyncio
import signal
from contextlib import suppress

import structlog

from optix.config import get_settings
from optix.research.jepa_forecaster.registry import ForecastRegistry
from optix.research.jepa_forecaster.runtime import ForecasterRuntime
from optix.data.categories import category_for_event_ticker
from optix.execution.paper import PaperExecutor
from optix.kalshi.feed import FeedQuote, FeedTrade, KalshiFeed
from optix.kalshi.rest import KalshiREST
from optix.risk.limits import RiskManager

log = structlog.get_logger(__name__)


async def discover_target_markets(
    rest: KalshiREST, max_markets: int = 200
) -> dict[str, str]:
    """Return {ticker: category} for open markets in target categories.

    Paginates list_markets and assigns a category from event_ticker prefix.
    """
    s = get_settings()
    targets = s.target_category_set
    out: dict[str, str] = {}
    cursor: str | None = None
    pages = 0
    while len(out) < max_markets and pages < 20:
        page = await rest.list_markets(status="open", limit=200, cursor=cursor)
        markets = page.get("markets", []) or []
        for m in markets:
            ticker = m.get("ticker")
            event_ticker = m.get("event_ticker") or ""
            cat = category_for_event_ticker(event_ticker)
            if ticker and cat in targets and cat != "Finance":
                out[ticker] = cat
                if len(out) >= max_markets:
                    break
        cursor = page.get("cursor")
        pages += 1
        if not cursor:
            break
    return out


async def settlement_watcher(
    rest: KalshiREST, paper: PaperExecutor, poll_s: float = 60.0
) -> None:
    """Periodically check our open positions for resolution and settle."""
    while True:
        try:
            tickers = list(paper.state.positions.keys())
            for ticker in tickers:
                with suppress(Exception):
                    detail = await rest.get_market(ticker)
                    market = detail.get("market", {})
                    result = market.get("result")
                    status = market.get("status")
                    if status == "settled" and result in {"yes", "no"}:
                        pnl = paper.settle(ticker, result)
                        log.info("paper.settled", ticker=ticker, result=result, pnl_usd=pnl)
        except Exception as e:
            log.warning("settlement_watcher.error", error=str(e))
        await asyncio.sleep(poll_s)


async def run(max_markets: int = 200) -> None:
    s = get_settings()
    if s.optix_live:
        log.warning("optix.live_mode_active")
        raise NotImplementedError(
            "Live order placement is intentionally not wired in v0. "
            "Implement and audit the order router before flipping OPTIX_LIVE=1."
        )

    rest = KalshiREST()
    log.info("optix.discovering_markets", target_categories=sorted(s.target_category_set))
    market_cats = await discover_target_markets(rest, max_markets=max_markets)
    log.info("optix.markets_resolved", count=len(market_cats))
    if not market_cats:
        log.warning("optix.no_target_markets_open", note="check categories.py prefix map")
        await rest.aclose()
        return

    risk = RiskManager()
    forecaster: ForecasterRuntime | None = None
    if s.optix_forecast_mode != "structural_only" and s.optix_forecast_artifact_id:
        mp = ForecastRegistry().model_path(s.optix_forecast_artifact_id)
        if mp.exists():
            forecaster = ForecasterRuntime.from_joblib(mp)
            log.info("optix.forecaster_loaded", artifact_id=s.optix_forecast_artifact_id)
        else:
            log.warning(
                "optix.forecaster_missing",
                artifact_id=s.optix_forecast_artifact_id,
                path=str(mp),
            )

    paper = PaperExecutor(risk=risk, market_categories=market_cats, forecaster=forecaster)
    feed = KalshiFeed()

    stop_event = asyncio.Event()

    def _stop(*_):
        stop_event.set()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, _stop)

    settler = asyncio.create_task(settlement_watcher(rest, paper))

    try:
        async for event in feed.stream(list(market_cats.keys())):
            if stop_event.is_set():
                break
            if isinstance(event, FeedQuote):
                paper.on_quote(event)
            elif isinstance(event, FeedTrade):
                paper.on_trade(event)
    finally:
        settler.cancel()
        with suppress(asyncio.CancelledError):
            await settler
        await rest.aclose()
        paper.close()
        log.info("optix.shutdown", snapshot=paper.snapshot())


if __name__ == "__main__":
    asyncio.run(run())
