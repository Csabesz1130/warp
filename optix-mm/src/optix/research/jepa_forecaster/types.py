"""Typed contracts for forecasts, manifests, and gate results."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ForecastHorizon(str, Enum):
    """Forecast horizons (v1 uses snapshot-at-trade; horizons reserved for future)."""

    SNAPSHOT = "snapshot"
    H1 = "1h"
    H24 = "24h"


class ForecastMode(str, Enum):
    """Runtime strategy mode for mixing structural alpha with forecasts."""

    STRUCTURAL_ONLY = "structural_only"
    HYBRID = "hybrid"
    FORECAST_ABLATION = "forecast_ablation"


@dataclass
class ForecastPoint:
    """Single probability output for a market at a point in time."""

    market_ticker: str
    horizon: ForecastHorizon
    p_yes: float
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GateResult:
    """Outcome of strict benchmark gates."""

    passed: bool
    brier_model: float
    brier_baseline: float
    brier_delta: float
    logloss_model: float
    logloss_baseline: float
    logloss_delta: float
    ece_model: float
    n_test: int
    categories_represented: int
    messages: list[str] = field(default_factory=list)


@dataclass
class ArtifactManifest:
    """Registered artifact with reproducibility and gate linkage."""

    artifact_id: str
    created_at_utc: str
    dataset_hash: str
    baseline_snapshot_id: str
    model_backend: str
    feature_names: list[str]
    horizon: str
    gate: GateResult | None
    metrics_path: str | None = None
    approved: bool = False
    encoder_extra_dim: int = 0  # multimodal padding dims used at train time

    def to_dict(self) -> dict[str, Any]:
        g = self.gate
        return {
            "artifact_id": self.artifact_id,
            "created_at_utc": self.created_at_utc,
            "dataset_hash": self.dataset_hash,
            "baseline_snapshot_id": self.baseline_snapshot_id,
            "model_backend": self.model_backend,
            "feature_names": self.feature_names,
            "horizon": self.horizon,
            "metrics_path": self.metrics_path,
            "approved": self.approved,
            "encoder_extra_dim": self.encoder_extra_dim,
            "gate": None
            if g is None
            else {
                "passed": g.passed,
                "brier_model": g.brier_model,
                "brier_baseline": g.brier_baseline,
                "brier_delta": g.brier_delta,
                "logloss_model": g.logloss_model,
                "logloss_baseline": g.logloss_baseline,
                "logloss_delta": g.logloss_delta,
                "ece_model": g.ece_model,
                "n_test": g.n_test,
                "categories_represented": g.categories_represented,
                "messages": g.messages,
            },
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ArtifactManifest":
        gd = d.get("gate")
        gate = None
        if gd:
            gate = GateResult(
                passed=gd["passed"],
                brier_model=gd["brier_model"],
                brier_baseline=gd["brier_baseline"],
                brier_delta=gd["brier_delta"],
                logloss_model=gd["logloss_model"],
                logloss_baseline=gd["logloss_baseline"],
                logloss_delta=gd["logloss_delta"],
                ece_model=gd["ece_model"],
                n_test=gd["n_test"],
                categories_represented=gd["categories_represented"],
                messages=list(gd.get("messages", [])),
            )
        return cls(
            artifact_id=d["artifact_id"],
            created_at_utc=d["created_at_utc"],
            dataset_hash=d["dataset_hash"],
            baseline_snapshot_id=d["baseline_snapshot_id"],
            model_backend=d["model_backend"],
            feature_names=list(d["feature_names"]),
            horizon=d["horizon"],
            gate=gate,
            metrics_path=d.get("metrics_path"),
            approved=d.get("approved", False),
            encoder_extra_dim=int(d.get("encoder_extra_dim", 0)),
        )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
