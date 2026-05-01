"""Evaluate an existing saved model blob against holdout split (no registration)."""

from __future__ import annotations

import json
from pathlib import Path

import joblib

from optix.config import get_settings
from optix.research.jepa_forecaster.baselines import implied_probability_from_yes_cents
from optix.research.jepa_forecaster.datasets import build_market_supervised_frame
from optix.research.jepa_forecaster.gates import run_gates
from optix.research.jepa_forecaster.splits import temporal_split_markets
from optix.research.jepa_forecaster.train import frame_to_xy


def evaluate_joblib(model_path: Path) -> dict:
    s = get_settings()
    blob = joblib.load(model_path)
    pipe = blob["pipeline"]
    enc_dim = int(blob.get("encoder_extra_dim", 0))

    df = build_market_supervised_frame(
        price_lo=s.optix_longshot_price_lo_cents,
        price_hi=s.optix_longshot_price_hi_cents,
        min_market_volume=100,
        encoder_extra_dim=enc_dim,
    )
    _train, _val, test_df = temporal_split_markets(
        df,
        train_frac=s.optix_forecast_train_frac,
        val_frac=s.optix_forecast_val_frac,
    )
    X_test, y_test, yes_prices_test, cats_test = frame_to_xy(test_df, enc_dim)
    p_model = pipe.predict_proba(X_test)[:, 1]
    p_base = implied_probability_from_yes_cents(yes_prices_test)
    gate = run_gates(y_test, p_model, p_base, cats_test)

    return {
        "n_test": int(len(y_test)),
        "gate_passed": gate.passed,
        "brier_model": gate.brier_model,
        "brier_baseline": gate.brier_baseline,
        "brier_delta": gate.brier_delta,
        "logloss_model": gate.logloss_model,
        "logloss_baseline": gate.logloss_baseline,
        "logloss_delta": gate.logloss_delta,
        "ece_model": gate.ece_model,
        "categories_represented": gate.categories_represented,
        "messages": gate.messages,
    }


def evaluate_joblib_to_json(model_path: Path, out_json: Path) -> None:
    report = evaluate_joblib(model_path)
    out_json.write_text(json.dumps(report, indent=2))
