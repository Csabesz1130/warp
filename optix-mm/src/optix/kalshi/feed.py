"""Kalshi WebSocket v2 feed.

Subscribes to `trade` and `orderbook_delta` channels for the markets we
care about and emits typed events into an asyncio.Queue. The strategy
runner consumes from that queue.

We use raw `websockets` rather than a third-party trader library to keep
dependencies tight and the auth code auditable.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

import structlog
import websockets

from optix.config import get_settings
from optix.kalshi.auth import auth_headers, load_private_key

log = structlog.get_logger(__name__)


@dataclass
class FeedTrade:
    ticker: str
    yes_price: int
    no_price: int
    count: int
    taker_side: str
    ts_ms: int


@dataclass
class FeedQuote:
    """Top-of-book snapshot for one market.

    For v0 we keep this simple: top bid/ask on YES side, derive NO from p+q=100.
    """
    ticker: str
    yes_bid: int | None
    yes_ask: int | None
    no_bid: int | None
    no_ask: int | None


class KalshiFeed:
    def __init__(self) -> None:
        s = get_settings()
        self._url = s.kalshi_ws_url
        self._key_id = s.kalshi_key_id
        self._key = load_private_key(s.kalshi_private_key_path) if s.kalshi_key_id else None
        self._msg_id = 1
        self._tickers: list[str] = []

    def _ws_path(self) -> str:
        return urlparse(self._url).path  # /trade-api/ws/v2

    async def _connect(self) -> Any:
        if self._key is None:
            raise RuntimeError(
                "KALSHI_KEY_ID + private key required to connect to WebSocket."
            )
        headers = auth_headers(self._key_id, self._key, "GET", self._ws_path())
        return await websockets.connect(self._url, additional_headers=headers, ping_interval=20)

    async def _subscribe(self, ws: Any, channel: str, tickers: list[str]) -> None:
        msg = {
            "id": self._msg_id,
            "cmd": "subscribe",
            "params": {"channels": [channel], "market_tickers": tickers},
        }
        self._msg_id += 1
        await ws.send(json.dumps(msg))

    async def stream(self, market_tickers: list[str]) -> AsyncIterator[FeedTrade | FeedQuote]:
        """Yield FeedTrade and FeedQuote events as they arrive.

        Reconnects on transient errors with exponential backoff.
        """
        self._tickers = market_tickers
        backoff = 1.0
        while True:
            try:
                async with await self._connect() as ws:
                    log.info("kalshi.ws.connected", n_tickers=len(market_tickers))
                    backoff = 1.0
                    await self._subscribe(ws, "trade", market_tickers)
                    await self._subscribe(ws, "orderbook_delta", market_tickers)
                    async for raw in ws:
                        event = self._parse(raw)
                        if event is not None:
                            yield event
            except (websockets.ConnectionClosed, OSError, asyncio.TimeoutError) as e:
                log.warning("kalshi.ws.reconnecting", error=str(e), backoff_s=backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60.0)

    def _parse(self, raw: str | bytes) -> FeedTrade | FeedQuote | None:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            log.warning("kalshi.ws.bad_json", raw=str(raw)[:200])
            return None

        if data.get("type") == "trade":
            m = data.get("msg", {})
            return FeedTrade(
                ticker=m.get("market_ticker", ""),
                yes_price=int(m.get("yes_price", 0)),
                no_price=int(m.get("no_price", 100 - int(m.get("yes_price", 0)))),
                count=int(m.get("count", 0)),
                taker_side=str(m.get("taker_side", "")),
                ts_ms=int(m.get("ts", 0)) * 1000 if m.get("ts") else 0,
            )

        if data.get("type") in {"orderbook_snapshot", "orderbook_delta"}:
            m = data.get("msg", {})
            yes_levels = m.get("yes") or []
            no_levels = m.get("no") or []

            def best_bid_ask(levels: list[list[int]]) -> tuple[int | None, int | None]:
                if not levels:
                    return None, None
                # Kalshi convention: levels are [price_cents, size]; bids on
                # this side, asks derived from the complementary side.
                prices = sorted({int(p) for p, _ in levels})
                return (prices[-1] if prices else None, prices[0] if prices else None)

            yes_bid, yes_ask = best_bid_ask(yes_levels)
            no_bid, no_ask = best_bid_ask(no_levels)
            return FeedQuote(
                ticker=m.get("market_ticker", ""),
                yes_bid=yes_bid,
                yes_ask=yes_ask,
                no_bid=no_bid,
                no_ask=no_ask,
            )
        return None
