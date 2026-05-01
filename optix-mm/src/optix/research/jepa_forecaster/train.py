"""Train sklearn prototype forecaster (swap for PyTorch JEPA encoder later)."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import joblib
import numpy as np
import polars as pl
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from optix.config import get_settings
from optix.research.jepa_forecaster.baselines import baseline_snapshot_id, implied_probability_from_yes_cents
from optix.research.jepa_forecaster.datasets import build_market_supervised_frame, frame_content_hash
from optix.research.jepa_forecaster.features import feature_names, microstructure_vector_from_row
from optix.research.jepa_forecaster.gates import run_gates
from optix.research.jepa_forecaster.registry import ForecastRegistry
from optix.research.jepa_forecaster.splits import temporal_split_markets
from optix.research.jepa_forecaster.types import ArtifactManifest, ForecastHorizon, utc_now_iso


def frame_to_xy(df: pl.DataFrame, encoder_extra_dim: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    X_list: list[np.ndarray] = []
    y_list: list[int] = []
    prices: list[float] = []
    cats: list[str] = []
    for row in df.iter_rows(named=True):
        aux = row.get("aux_embedding") if encoder_extra_dim > 0 else None
        aux_vec = list(aux) if isinstance(aux, list) else None
        v = microstructure_vector_from_row(
            float(row["yes_price_last"]),
            float(row["yes_imbalance"]),
            float(row["total_vol"]),
            float(row["n_trades"]),
            float(row["yes_price_mean"]),
            str(row["category"]),
            encoder_extra_dim=encoder_extra_dim,
            aux_vector=aux_vec,
        )
        X_list.append(v)
        y_list.append(int(row["label_yes"]))
        prices.append(float(row["yes_price_last"]))
        cats.append(str(row["category"]))
    return np.stack(X_list), np.array(y_list, dtype=np.int64), np.array(prices), cats


def train_and_maybe_register(
    *,
    encoder_extra_dim: int = 0,
    register: bool = False,
    output_dir: Path | None = None,
) -> tuple[ArtifactManifest, Path]:
    """Train on Becker market aggregates, evaluate gates on holdout, optionally register."""
    s = get_settings()
    df = build_market_supervised_frame(
        price_lo=s.optix_longshot_price_lo_cents,
        price_hi=s.optix_longshot_price_hi_cents,
        min_market_volume=100,
        encoder_extra_dim=encoder_extra_dim,
    )
    train_df, val_df, test_df = temporal_split_markets(
        df,
        train_frac=s.optix_forecast_train_frac,
        val_frac=s.optix_forecast_val_frac,
    )

    X_train, y_train, _, _ = frame_to_xy(train_df, encoder_extra_dim)
    X_test, y_test, yes_prices_test, cats_test = frame_to_xy(test_df, encoder_extra_dim)

    if len(np.unique(y_train)) < 2:
        raise ValueError("Training set needs both classes for classifier")

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        (
            "clf",
            MLPClassifier(
                hidden_layer_sizes=s.forecast_mlp_hidden_tuple,
                max_iter=int(s.optix_forecast_mlp_max_iter),
                random_state=42,
                early_stopping=True,
                validation_fraction=0.1,
                n_iter_no_change=10,
            ),
        ),
    ])
    pipe.fit(X_train, y_train)

    p_model = pipe.predict_proba(X_test)[:, 1]
    p_base = implied_probability_from_yes_cents(yes_prices_test)

    gate = run_gates(y_test, p_model, p_base, cats_test)
    approved = gate.passed

    artifact_id = uuid.uuid4().hex[:12]
    fnames = feature_names(encoder_extra_dim)
    ds_hash = frame_content_hash(df)
    snap_id = baseline_snapshot_id(p_base)

    metrics = {
        "artifact_id": artifact_id,
        "n_train": int(train_df.height),
        "n_val": int(val_df.height),
        "n_test": int(test_df.height),
        "dataset_hash": ds_hash,
        "baseline_snapshot_id": snap_id,
        "gate": {
            "passed": gate.passed,
            "brier_model": gate.brier_model,
            "brier_baseline": gate.brier_baseline,
            "brier_delta": gate.brier_delta,
            "logloss_model": gate.logloss_model,
            "logloss_baseline": gate.logloss_baseline,
            "logloss_delta": gate.logloss_delta,
            "ece_model": gate.ece_model,
            "messages": gate.messages,
        },
    }

    out = output_dir or (s.optix_log_dir / "jepa-train")
    out.mkdir(parents=True, exist_ok=True)
    metrics_path = out / f"metrics-{artifact_id}.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))

    blob = {
        "pipeline": pipe,
        "feature_names": fnames,
        "encoder_extra_dim": encoder_extra_dim,
        "artifact_id": artifact_id,
    }
    model_path = out / f"forecaster-{artifact_id}.joblib"
    joblib.dump(blob, model_path)

    manifest = ArtifactManifest(
        artifact_id=artifact_id,
        created_at_utc=utc_now_iso(),
        dataset_hash=ds_hash,
        baseline_snapshot_id=snap_id,
        model_backend="sklearn_mlp_v1",
        feature_names=fnames,
        horizon=ForecastHorizon.SNAPSHOT.value,
        gate=gate,
        metrics_path=str(metrics_path),
        approved=approved,
        encoder_extra_dim=encoder_extra_dim,
    )

    if register and approved:
        reg = ForecastRegistry()
        reg.register_approved(manifest, model_src=model_path, metrics_src=metrics_path)

    return manifest, model_path
