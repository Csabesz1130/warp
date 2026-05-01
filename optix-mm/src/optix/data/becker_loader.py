"""DuckDB-based loader over Becker's prediction-market-analysis dataset.

Becker (2026) "The Microstructure of Wealth Transfer in Prediction Markets"
publishes the schema for kalshi/markets and kalshi/trades parquet files. We
treat them as read-only. All queries go through DuckDB so we can stream
without loading everything into RAM.
"""

from __future__ import annotations

from dataclasses import dataclass

import duckdb
import polars as pl

from optix.config import get_settings


@dataclass(frozen=True)
class BeckerDataPaths:
    markets_glob: str
    trades_glob: str

    @classmethod
    def from_settings(cls) -> "BeckerDataPaths":
        s = get_settings()
        if not s.kalshi_markets_dir.exists():
            raise FileNotFoundError(
                f"Becker markets dir not found at {s.kalshi_markets_dir}. "
                "Run Becker's downloader first (see README)."
            )
        return cls(
            markets_glob=str(s.kalshi_markets_dir / "*.parquet"),
            trades_glob=str(s.kalshi_trades_dir / "*.parquet"),
        )


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    # Modest threads to be friendly on a laptop. Bump on a workstation.
    con.execute("SET threads = 4")
    con.execute("SET memory_limit = '8GB'")
    return con


def resolved_market_count(con: duckdb.DuckDBPyConnection, paths: BeckerDataPaths) -> int:
    q = f"""
        SELECT COUNT(*)
        FROM '{paths.markets_glob}'
        WHERE result IS NOT NULL AND result IN ('yes', 'no')
    """
    return con.execute(q).fetchone()[0]


def trade_count(con: duckdb.DuckDBPyConnection, paths: BeckerDataPaths) -> int:
    q = f"SELECT COUNT(*) FROM '{paths.trades_glob}'"
    return con.execute(q).fetchone()[0]


def trades_with_outcomes(
    con: duckdb.DuckDBPyConnection,
    paths: BeckerDataPaths,
    price_lo: int = 1,
    price_hi: int = 99,
    min_market_volume: int = 100,
) -> pl.DataFrame:
    """Join trades to resolved-market outcomes and filter as in Becker (2026).

    Returns a polars DataFrame with the trade-level fields we need:
      ticker, taker_side, yes_price, no_price, count, ts, result
    """
    q = f"""
        WITH market_volume AS (
            SELECT ticker, SUM(count) AS total_contracts
            FROM '{paths.trades_glob}'
            GROUP BY ticker
        ),
        resolved AS (
            SELECT ticker, result, event_ticker
            FROM '{paths.markets_glob}'
            WHERE result IN ('yes', 'no')
        )
        SELECT
            t.ticker,
            t.taker_side,
            t.yes_price,
            t.no_price,
            t.count,
            t.created_time AS ts,
            r.result,
            r.event_ticker
        FROM '{paths.trades_glob}' t
        JOIN resolved r USING (ticker)
        JOIN market_volume mv USING (ticker)
        WHERE mv.total_contracts >= {min_market_volume}
          AND t.yes_price BETWEEN {price_lo} AND {price_hi}
    """
    return con.execute(q).pl()


def category_volume(
    con: duckdb.DuckDBPyConnection, paths: BeckerDataPaths
) -> pl.DataFrame:
    """Volume by Kalshi event-ticker prefix (rough category proxy)."""
    q = f"""
        SELECT
            CASE
                WHEN event_ticker IS NULL OR event_ticker = ''
                THEN 'independent'
                ELSE regexp_extract(event_ticker, '^([A-Z0-9]+)', 1)
            END AS prefix,
            COUNT(*) AS market_count
        FROM '{paths.markets_glob}'
        GROUP BY prefix
        ORDER BY market_count DESC
    """
    return con.execute(q).pl()
