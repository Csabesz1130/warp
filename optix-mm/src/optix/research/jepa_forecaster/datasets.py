"""Market-level supervised dataset from Becker parquet via DuckDB."""

from __future__ import annotations

import hashlib
import io

import polars as pl

from optix.data.becker_loader import BeckerDataPaths, connect, trades_with_outcomes
from optix.data.categories import category_for_event_ticker


def build_market_supervised_frame(
    price_lo: int = 1,
    price_hi: int = 15,
    min_market_volume: int = 100,
    *,
    encoder_extra_dim: int = 0,
) -> pl.DataFrame:
    """One row per market: tape aggregates + label (YES resolved).

    Optional ``encoder_extra_dim`` adds zero-filled aux columns for multimodal alignment.
    """
    paths = BeckerDataPaths.from_settings()
    con = connect()
    trades = trades_with_outcomes(
        con,
        paths,
        price_lo=price_lo,
        price_hi=price_hi,
        min_market_volume=min_market_volume,
    )
    trades = trades.sort("ts")
    trades = trades.with_columns(
        pl.col("event_ticker")
        .map_elements(
            lambda x: category_for_event_ticker(x),
            return_dtype=pl.Utf8,
        )
        .alias("category"),
    )

    tot = pl.col("count").sum()
    yes_vol = ((pl.col("taker_side") == "yes").cast(pl.Float64) * pl.col("count")).sum()
    weighted_yes = (pl.col("yes_price").cast(pl.Float64) * pl.col("count")).sum()

    agg = trades.group_by("ticker").agg([
        pl.col("result").last().alias("result"),
        pl.col("event_ticker").last().alias("event_ticker"),
        pl.col("category").last().alias("category"),
        pl.col("yes_price").last().alias("yes_price_last"),
        (yes_vol / tot.clip(lower_bound=1)).alias("yes_imbalance"),
        (weighted_yes / tot.clip(lower_bound=1)).alias("yes_price_mean"),
        tot.alias("total_vol"),
        pl.len().alias("n_trades"),
        pl.col("ts").max().alias("last_ts"),
    ])
    out = agg.with_columns([
        (pl.col("result") == "yes").cast(pl.Int8).alias("label_yes"),
    ]).drop_nulls(["label_yes"])

    if encoder_extra_dim > 0:
        # Placeholder for fused video/text embeddings; zeros until adapters ingest assets.
        out = out.with_columns(
            pl.lit([[0.0] * encoder_extra_dim]).alias("aux_embedding"),
        )

    return out


def frame_content_hash(df: pl.DataFrame) -> str:
    """SHA256 over sorted ticker + last_ts + label for manifest pinning."""
    key = df.select(["ticker", "last_ts", "label_yes"]).sort(["last_ts", "ticker"])
    buf = io.BytesIO()
    key.write_csv(buf)
    return hashlib.sha256(buf.getvalue()).hexdigest()[:24]
