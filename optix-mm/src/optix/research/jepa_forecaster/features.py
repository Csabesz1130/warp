"""Feature builders: microstructure (required) + optional multimodal padding."""

from __future__ import annotations

from typing import Any

import numpy as np

from optix.strategy.signals import TradeTick

# Fixed category slots for one-hot (must match training export order).
CATEGORY_ORDER: list[str] = [
    "Sports",
    "Entertainment",
    "Media",
    "WorldEvents",
    "Crypto",
    "Weather",
    "Politics",
    "Other",
]


def feature_names(encoder_extra_dim: int = 0) -> list[str]:
    base = [
        "yes_price_norm",
        "yes_imbalance",
        "log1p_total_vol",
        "n_trades_norm",
        "yes_price_mean_norm",
    ] + [f"cat_{c}" for c in CATEGORY_ORDER]
    extra = [f"aux_{i}" for i in range(encoder_extra_dim)]
    return base + extra


def category_one_hot(category: str) -> list[float]:
    vec = [0.0] * len(CATEGORY_ORDER)
    cat = category if category in CATEGORY_ORDER else "Other"
    idx = CATEGORY_ORDER.index(cat)
    vec[idx] = 1.0
    return vec


def microstructure_vector_from_ticks(
    ticks: list[TradeTick],
    category: str,
    *,
    encoder_extra_dim: int = 0,
    aux_vector: list[float] | None = None,
) -> np.ndarray:
    """Build feature vector from a list of TradeTicks (chronological)."""
    cat = category if category in CATEGORY_ORDER else "Other"
    if not ticks:
        yes_price_last = 0.0
        imb = 0.5
        total_vol = 0.0
        n = 0
        mean_yes = 0.0
    else:
        yes_price_last = float(ticks[-1].yes_price_cents)
        total_vol = float(sum(t.count for t in ticks))
        n = len(ticks)
        yes_vol = float(sum(t.count for t in ticks if t.taker_side == "yes"))
        imb = yes_vol / total_vol if total_vol > 0 else 0.5
        mean_yes = float(sum(t.yes_price_cents * t.count for t in ticks)) / max(total_vol, 1.0)

    base = [
        yes_price_last / 100.0,
        imb,
        np.log1p(total_vol),
        min(n, 100) / 100.0,
        mean_yes / 100.0,
    ] + category_one_hot(cat)

    aux = [0.0] * encoder_extra_dim
    if aux_vector:
        for i in range(min(encoder_extra_dim, len(aux_vector))):
            aux[i] = float(aux_vector[i])

    return np.array(base + aux, dtype=np.float64)


def microstructure_vector_from_row(
    yes_price_last: float,
    yes_imbalance: float,
    total_vol: float,
    n_trades: float,
    yes_price_mean: float,
    category: str,
    *,
    encoder_extra_dim: int = 0,
    aux_vector: list[float] | None = None,
) -> np.ndarray:
    """Vector from aggregated market row (training table)."""
    cat = category if category in CATEGORY_ORDER else "Other"
    base = [
        yes_price_last / 100.0,
        yes_imbalance,
        np.log1p(total_vol),
        min(n_trades, 100.0) / 100.0,
        yes_price_mean / 100.0,
    ] + category_one_hot(cat)

    aux = [0.0] * encoder_extra_dim
    if aux_vector:
        for i in range(min(encoder_extra_dim, len(aux_vector))):
            aux[i] = float(aux_vector[i])

    return np.array(base + aux, dtype=np.float64)


def dataset_row_aux(aux_json: Any, encoder_extra_dim: int) -> list[float] | None:
    """Parse optional multimodal aux from Polars struct/list column."""
    if aux_json is None or encoder_extra_dim <= 0:
        return None
    if isinstance(aux_json, list):
        return [float(x) for x in aux_json[:encoder_extra_dim]]
    return None
