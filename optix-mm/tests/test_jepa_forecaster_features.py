"""Feature builder determinism."""

from __future__ import annotations

from collections import deque

import numpy as np

from optix.research.jepa_forecaster.features import (
    feature_names,
    microstructure_vector_from_ticks,
)
from optix.strategy.signals import TradeTick


def test_microstructure_vector_deterministic_for_same_ticks():
    ticks = [
        TradeTick(ts_ms=0, yes_price_cents=5, taker_side="yes", count=1),
        TradeTick(ts_ms=1, yes_price_cents=6, taker_side="no", count=2),
    ]
    a = microstructure_vector_from_ticks(ticks, "Sports")
    b = microstructure_vector_from_ticks(list(deque(ticks)), "Sports")
    assert np.allclose(a, b)


def test_feature_names_length_matches_vector():
    enc = 4
    ticks = [TradeTick(0, 5, "yes", 1)]
    v = microstructure_vector_from_ticks(ticks, "Media", encoder_extra_dim=enc)
    names = feature_names(enc)
    assert len(names) == len(v)


def test_unknown_category_maps_to_other_slot():
    ticks = [TradeTick(0, 5, "yes", 1)]
    v = microstructure_vector_from_ticks(ticks, "WeirdCat")
    names = feature_names(0)
    idx = names.index("cat_Other")
    assert v[idx] == 1.0
