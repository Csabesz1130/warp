"""Forecast artifact registry IO."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pytest

from optix.research.jepa_forecaster.registry import ForecastRegistry
from optix.research.jepa_forecaster.types import ArtifactManifest, GateResult, utc_now_iso


def _approved_manifest(aid: str) -> ArtifactManifest:
    gate = GateResult(
        passed=True,
        brier_model=0.1,
        brier_baseline=0.15,
        brier_delta=0.05,
        logloss_model=0.5,
        logloss_baseline=0.6,
        logloss_delta=0.1,
        ece_model=0.05,
        n_test=500,
        categories_represented=5,
        messages=[],
    )
    return ArtifactManifest(
        artifact_id=aid,
        created_at_utc=utc_now_iso(),
        dataset_hash="deadbeef",
        baseline_snapshot_id="snap",
        model_backend="test",
        feature_names=["yes_price_norm"],
        horizon="snapshot",
        gate=gate,
        metrics_path="metrics.json",
        approved=True,
    )


def test_register_approved_roundtrip(tmp_path: Path) -> None:
    reg = ForecastRegistry(root=tmp_path / "artifacts")
    m = _approved_manifest("abc123def456")
    model_src = tmp_path / "src-model.joblib"
    joblib.dump({"pipeline": None}, model_src)
    metrics_src = tmp_path / "metrics.json"
    metrics_src.write_text(json.dumps({"ok": True}))

    reg.register_approved(m, model_src=model_src, metrics_src=metrics_src)

    loaded = reg.load_manifest("abc123def456")
    assert loaded.approved
    assert loaded.gate is not None and loaded.gate.passed
    assert reg.model_path("abc123def456").exists()
    assert reg.manifest_path("abc123def456").exists()


def test_register_rejects_unapproved(tmp_path: Path) -> None:
    reg = ForecastRegistry(root=tmp_path / "artifacts")
    gate = GateResult(
        passed=False,
        brier_model=0.2,
        brier_baseline=0.15,
        brier_delta=-0.05,
        logloss_model=0.7,
        logloss_baseline=0.6,
        logloss_delta=-0.1,
        ece_model=0.2,
        n_test=100,
        categories_represented=3,
        messages=["fail"],
    )
    m = ArtifactManifest(
        artifact_id="bad",
        created_at_utc=utc_now_iso(),
        dataset_hash="x",
        baseline_snapshot_id="y",
        model_backend="test",
        feature_names=["a"],
        horizon="snapshot",
        gate=gate,
        approved=False,
    )
    with pytest.raises(ValueError):
        reg.register_approved(m)


def test_latest_approved_id(tmp_path: Path) -> None:
    reg = ForecastRegistry(root=tmp_path / "artifacts")
    for aid in ("aaa111", "bbb222"):
        m = _approved_manifest(aid)
        model_src = tmp_path / f"{aid}.joblib"
        joblib.dump({"x": 1}, model_src)
        metrics_src = tmp_path / f"{aid}-m.json"
        metrics_src.write_text("{}")
        reg.register_approved(m, model_src=model_src, metrics_src=metrics_src)

    latest = reg.latest_approved_id()
    assert latest is not None
    loaded = reg.load_manifest(latest)
    assert loaded.approved and loaded.gate is not None and loaded.gate.passed
