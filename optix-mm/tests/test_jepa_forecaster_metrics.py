"""Unit tests for probability metrics and EV blending helpers."""

from __future__ import annotations

import numpy as np
import pytest

from optix.research.jepa_forecaster.eval_metrics import (
    brier_score,
    expected_calibration_error,
    log_loss_binary,
    sharpness,
)
from optix.research.jepa_forecaster.types import ForecastMode
from optix.strategy.signals import effective_yes_winrate


def test_brier_perfect_predictions():
    y = np.array([0, 1, 0, 1], dtype=np.int64)
    p = np.array([0.01, 0.99, 0.02, 0.98])
    assert brier_score(y, p) < 0.01


def test_log_loss_matches_manual_binary():
    y = np.array([1, 0], dtype=np.int64)
    p = np.array([0.5, 0.5])
    assert log_loss_binary(y, p) == pytest.approx(np.log(2))


def test_sharpness_bounded():
    p = np.linspace(0.1, 0.9, 9)
    s = sharpness(p)
    assert 0 < s <= 0.25


def test_ece_non_negative():
    y = np.array([0, 1] * 50, dtype=np.int64)
    p = np.full(100, 0.5)
    assert expected_calibration_error(y, p, n_bins=10) >= 0


def test_effective_yes_winrate_hybrid_blends():
    assert effective_yes_winrate(0.10, 0.02, ForecastMode.HYBRID, 0.5) == pytest.approx(0.06)


def test_effective_yes_winrate_structural_only_ignores_forecast():
    assert effective_yes_winrate(0.10, 0.99, ForecastMode.STRUCTURAL_ONLY, 0.5) == pytest.approx(0.10)


def test_effective_yes_winrate_ablation_prefers_forecast():
    assert effective_yes_winrate(0.10, 0.02, ForecastMode.FORECAST_ABLATION, 0.5) == pytest.approx(0.02)
