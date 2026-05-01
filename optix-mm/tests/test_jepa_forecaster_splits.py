"""Deterministic splits and dataset hashing."""

from __future__ import annotations

import polars as pl

from optix.research.jepa_forecaster.datasets import frame_content_hash
from optix.research.jepa_forecaster.splits import dataset_content_hash, temporal_split_markets


def test_temporal_split_partitions_all_rows():
    df = pl.DataFrame({
        "last_ts": list(range(100)),
        "ticker": [f"M{i}" for i in range(100)],
        "label_yes": [i % 2 for i in range(100)],
    })
    tr, va, te = temporal_split_markets(df, train_frac=0.70, val_frac=0.15)
    assert tr.height + va.height + te.height == 100


def test_dataset_content_hash_stable():
    df = pl.DataFrame({"b": [2, 1], "a": [1, 2]})
    assert dataset_content_hash(df) == dataset_content_hash(df)


def test_frame_content_hash_stable():
    df = pl.DataFrame({
        "ticker": ["A", "B"],
        "last_ts": [1, 2],
        "label_yes": [0, 1],
    })
    assert frame_content_hash(df) == frame_content_hash(df)
