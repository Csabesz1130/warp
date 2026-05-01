"""Frozen baselines (implied probability from mid/last trade)."""

from __future__ import annotations

import hashlib

import numpy as np


def implied_probability_from_yes_cents(yes_price_cents: np.ndarray) -> np.ndarray:
    """Kalshi-style implied YES probability from price in cents."""
    p = yes_price_cents.astype(np.float64) / 100.0
    return np.clip(p, 1e-6, 1.0 - 1e-6)


def baseline_snapshot_id(p_implied: np.ndarray) -> str:
    """Stable id for manifest linkage."""
    b = p_implied.astype(np.float64).tobytes()
    return hashlib.sha256(b).hexdigest()[:16]
