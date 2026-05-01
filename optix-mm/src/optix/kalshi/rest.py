"""Read-only REST client for Kalshi.

We deliberately do NOT implement order placement here in v0. Live order
placement happens through `execution.live_runner` which composes this
REST client and gates every order behind the `OPTIX_LIVE` flag.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import httpx

from optix.config import get_settings
from optix.kalshi.auth import auth_headers, load_private_key


class KalshiREST:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        s = get_settings()
        self._base = s.kalshi_api_base
        self._key_id = s.kalshi_key_id
        self._client = client or httpx.AsyncClient(timeout=15.0, follow_redirects=True)
        self._key = load_private_key(s.kalshi_private_key_path) if s.kalshi_key_id else None

    async def aclose(self) -> None:
        await self._client.aclose()

    def _path_only(self, url: str) -> str:
        return urlparse(url).path

    def _headers(self, method: str, full_url: str) -> dict[str, str]:
        if self._key is None:
            return {"Accept": "application/json"}
        return auth_headers(self._key_id, self._key, method, self._path_only(full_url))

    async def get(self, route: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self._base}{route}"
        headers = self._headers("GET", url)
        r = await self._client.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json()

    # Convenience wrappers ---------------------------------------------------

    async def list_markets(
        self,
        status: str = "open",
        limit: int = 1000,
        cursor: str | None = None,
        event_ticker: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"status": status, "limit": limit}
        if cursor:
            params["cursor"] = cursor
        if event_ticker:
            params["event_ticker"] = event_ticker
        return await self.get("/markets", params=params)

    async def get_orderbook(self, ticker: str, depth: int = 10) -> dict[str, Any]:
        return await self.get(f"/markets/{ticker}/orderbook", params={"depth": depth})

    async def get_market(self, ticker: str) -> dict[str, Any]:
        return await self.get(f"/markets/{ticker}")
