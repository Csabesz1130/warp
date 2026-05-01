"""Inference runtime for saved forecaster artifacts."""

from __future__ import annotations

from collections import deque
from pathlib import Path

import joblib
import numpy as np

from optix.research.jepa_forecaster.features import microstructure_vector_from_ticks
from optix.strategy.signals import TradeTick


class ForecasterRuntime:
    def __init__(
        self,
        pipeline,
        feature_names: list[str],
        encoder_extra_dim: int,
        artifact_id: str,
    ) -> None:
        self.pipeline = pipeline
        self.feature_names = feature_names
        self.encoder_extra_dim = encoder_extra_dim
        self.artifact_id = artifact_id

    @classmethod
    def from_joblib(cls, path: Path | str) -> "ForecasterRuntime":
        blob = joblib.load(path)
        return cls(
            pipeline=blob["pipeline"],
            feature_names=list(blob["feature_names"]),
            encoder_extra_dim=int(blob.get("encoder_extra_dim", 0)),
            artifact_id=str(blob.get("artifact_id", "unknown")),
        )

    def predict_p_yes_from_ticks(
        self,
        ticks: deque[TradeTick] | list[TradeTick],
        category: str,
        *,
        aux_vector: list[float] | None = None,
    ) -> float:
        arr = microstructure_vector_from_ticks(
            list(ticks),
            category,
            encoder_extra_dim=self.encoder_extra_dim,
            aux_vector=aux_vector,
        )
        x = arr.reshape(1, -1)
        return float(self.pipeline.predict_proba(x)[0, 1])
