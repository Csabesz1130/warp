"""JEPA-Forecaster v1: calibrated probability layer with strict benchmark gates.

The production stack may swap the sklearn prototype encoder for a PyTorch JEPA
encoder; contracts (manifest, registry, gates) stay stable.
"""

from optix.research.jepa_forecaster.registry import ForecastRegistry
from optix.research.jepa_forecaster.types import ArtifactManifest, ForecastHorizon

__all__ = ["ArtifactManifest", "ForecastHorizon", "ForecastRegistry"]
