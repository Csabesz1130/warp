"""Local artifact registry: manifests + optional sklearn model blob."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from optix.config import get_settings
from optix.research.jepa_forecaster.types import ArtifactManifest


MANIFEST_NAME = "manifest.json"
MODEL_NAME = "forecaster.joblib"


class ForecastRegistry:
    """Paths under ``runs/jepa-artifacts/<artifact_id>/``."""

    def __init__(self, root: Path | None = None) -> None:
        s = get_settings()
        self.root = root if root is not None else (s.optix_log_dir / "jepa-artifacts")
        self.root.mkdir(parents=True, exist_ok=True)

    def artifact_dir(self, artifact_id: str) -> Path:
        return self.root / artifact_id

    def manifest_path(self, artifact_id: str) -> Path:
        return self.artifact_dir(artifact_id) / MANIFEST_NAME

    def model_path(self, artifact_id: str) -> Path:
        return self.artifact_dir(artifact_id) / MODEL_NAME

    def write_manifest(self, manifest: ArtifactManifest) -> Path:
        d = self.artifact_dir(manifest.artifact_id)
        d.mkdir(parents=True, exist_ok=True)
        path = d / MANIFEST_NAME
        path.write_text(json.dumps(manifest.to_dict(), indent=2))
        return path

    def load_manifest(self, artifact_id: str) -> ArtifactManifest:
        path = self.manifest_path(artifact_id)
        return ArtifactManifest.from_dict(json.loads(path.read_text()))

    def load_manifest_from_path(self, path: Path) -> ArtifactManifest:
        return ArtifactManifest.from_dict(json.loads(path.read_text()))

    def register_approved(
        self,
        manifest: ArtifactManifest,
        model_src: Path | None = None,
        metrics_src: Path | None = None,
    ) -> Path:
        """Persist manifest; copy model/metrics into artifact dir. Fail-closed if not approved."""
        if not manifest.approved or manifest.gate is None or not manifest.gate.passed:
            raise ValueError("register_approved requires manifest.approved and gate.passed")
        self.write_manifest(manifest)
        aid = manifest.artifact_id
        if model_src is not None:
            shutil.copy2(model_src, self.model_path(aid))
        if metrics_src is not None:
            dst = self.artifact_dir(aid) / metrics_src.name
            shutil.copy2(metrics_src, dst)
        return self.manifest_path(aid)

    def latest_approved_id(self) -> str | None:
        """Return most recently written approved artifact id, if any."""
        candidates: list[tuple[float, str]] = []
        if not self.root.exists():
            return None
        for child in self.root.iterdir():
            if not child.is_dir():
                continue
            mp = child / MANIFEST_NAME
            if not mp.exists():
                continue
            try:
                m = ArtifactManifest.from_dict(json.loads(mp.read_text()))
            except (json.JSONDecodeError, KeyError):
                continue
            if m.approved and m.gate and m.gate.passed:
                candidates.append((mp.stat().st_mtime, m.artifact_id))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]


def load_json_metrics(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())
