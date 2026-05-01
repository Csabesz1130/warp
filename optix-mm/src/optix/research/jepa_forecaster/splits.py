"""Deterministic time-based splits on market last-trade timestamps."""

from __future__ import annotations

import hashlib
import io

import polars as pl


def dataset_content_hash(df: pl.DataFrame, cols: list[str] | None = None) -> str:
    """Stable hash for manifest reproducibility."""
    use = df.select(sorted(cols or df.columns))
    buf = io.BytesIO()
    use.write_csv(buf)
    return hashlib.sha256(buf.getvalue()).hexdigest()[:24]


def temporal_split_markets(
    df: pl.DataFrame,
    *,
    train_frac: float = 0.70,
    val_frac: float = 0.15,
    seed: int = 42,
    last_ts_col: str = "last_ts",
) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    """Split rows by sorted ``last_ts`` (global timeline)."""
    if train_frac + val_frac >= 1.0:
        raise ValueError("train_frac + val_frac must be < 1")
    sorted_df = df.sort(last_ts_col)
    n = sorted_df.height
    i_train = int(n * train_frac)
    i_val = int(n * (train_frac + val_frac))
    _ = seed  # reserved for stratified extensions
    train = sorted_df.head(i_train)
    val = sorted_df.slice(i_train, max(0, i_val - i_train))
    test = sorted_df.slice(i_val, n - i_val)
    return train, val, test
