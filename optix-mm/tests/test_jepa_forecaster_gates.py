"""Strict gate policy vs implied-probability baseline."""

from __future__ import annotations

import numpy as np
import pytest

from optix.config import reset_settings
from optix.research.jepa_forecaster.gates import run_gates


def _relax_gate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPTIX_FORECAST_MIN_TEST_SAMPLES", "10")
    monkeypatch.setenv("OPTIX_FORECAST_MIN_CATEGORIES", "1")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_BRIER_DELTA_MIN", "0")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_LOGLOSS_DELTA_MIN", "0")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_MAX_ECE", "1")
    reset_settings()


def test_gates_pass_when_model_beats_flat_baseline(monkeypatch: pytest.MonkeyPatch) -> None:
    _relax_gate_env(monkeypatch)
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int64)
    p_b = np.full_like(y, 0.5, dtype=float)
    p_m = np.where(y == 1, 0.95, 0.05).astype(float)
    cats = ["Sports"] * len(y)
    g = run_gates(y, p_m, p_b, cats)
    assert g.passed
    assert g.brier_delta > 0
    assert g.logloss_delta > 0


def test_gates_fail_when_equal_to_baseline(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPTIX_FORECAST_MIN_TEST_SAMPLES", "10")
    monkeypatch.setenv("OPTIX_FORECAST_MIN_CATEGORIES", "1")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_BRIER_DELTA_MIN", "0.001")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_LOGLOSS_DELTA_MIN", "0.001")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_MAX_ECE", "1")
    reset_settings()
    y = np.ones(20, dtype=np.int64)
    p_b = np.full(20, 0.5)
    p_m = np.full(20, 0.5)
    cats = ["Sports"] * 20
    g = run_gates(y, p_m, p_b, cats)
    assert not g.passed


def test_gates_fail_low_category_coverage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPTIX_FORECAST_MIN_TEST_SAMPLES", "5")
    monkeypatch.setenv("OPTIX_FORECAST_MIN_CATEGORIES", "3")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_BRIER_DELTA_MIN", "0")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_LOGLOSS_DELTA_MIN", "0")
    monkeypatch.setenv("OPTIX_FORECAST_GATE_MAX_ECE", "1")
    reset_settings()
    y = np.array([0, 1, 0, 1, 0], dtype=np.int64)
    p_m = np.where(y == 1, 0.9, 0.1).astype(float)
    p_b = np.full_like(p_m, 0.5)
    cats = ["Sports"] * len(y)
    g = run_gates(y, p_m, p_b, cats)
    assert not g.passed
    assert any("categories_represented" in m for m in g.messages)
