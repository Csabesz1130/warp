"""Strict benchmark gates vs implied-price baseline."""

from __future__ import annotations

import numpy as np

from optix.config import get_settings
from optix.research.jepa_forecaster.eval_metrics import (
    brier_score,
    expected_calibration_error,
    log_loss_binary,
)
from optix.research.jepa_forecaster.types import GateResult


def count_categories_present(categories: list[str]) -> int:
    return len({c for c in categories if c})


def run_gates(
    y_test: np.ndarray,
    p_model: np.ndarray,
    p_baseline: np.ndarray,
    categories_test: list[str],
) -> GateResult:
    s = get_settings()
    msgs: list[str] = []

    n_test = int(len(y_test))
    if n_test < s.optix_forecast_min_test_samples:
        msgs.append(
            f"n_test={n_test} < optix_forecast_min_test_samples={s.optix_forecast_min_test_samples}"
        )

    cats = count_categories_present(categories_test)
    if cats < s.optix_forecast_min_categories:
        msgs.append(
            f"categories_represented={cats} < optix_forecast_min_categories="
            f"{s.optix_forecast_min_categories}"
        )

    br_m = brier_score(y_test, p_model)
    br_b = brier_score(y_test, p_baseline)
    ll_m = log_loss_binary(y_test, p_model)
    ll_b = log_loss_binary(y_test, p_baseline)
    ece_m = expected_calibration_error(y_test, p_model, n_bins=s.optix_forecast_ece_bins)

    br_delta = br_b - br_m
    ll_delta = ll_b - ll_m

    if br_delta < s.optix_forecast_gate_brier_delta_min:
        msgs.append(
            f"Brier improvement {br_delta:.6f} < required {s.optix_forecast_gate_brier_delta_min}"
        )
    if ll_delta < s.optix_forecast_gate_logloss_delta_min:
        msgs.append(
            f"log_loss improvement {ll_delta:.6f} < required "
            f"{s.optix_forecast_gate_logloss_delta_min}"
        )
    if ece_m > s.optix_forecast_gate_max_ece:
        msgs.append(f"ECE={ece_m:.4f} > max {s.optix_forecast_gate_max_ece}")

    passed = len(msgs) == 0

    return GateResult(
        passed=passed,
        brier_model=br_m,
        brier_baseline=br_b,
        brier_delta=br_delta,
        logloss_model=ll_m,
        logloss_baseline=ll_b,
        logloss_delta=ll_delta,
        ece_model=ece_m,
        n_test=n_test,
        categories_represented=cats,
        messages=msgs,
    )
