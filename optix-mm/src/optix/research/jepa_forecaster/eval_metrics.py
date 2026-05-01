"""Probability metrics: Brier, log-loss, ECE."""

from __future__ import annotations

import numpy as np


def clip_probs(p: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    return np.clip(p.astype(np.float64), eps, 1.0 - eps)


def brier_score(y_true: np.ndarray, p_hat: np.ndarray) -> float:
    y = y_true.astype(np.float64)
    p = clip_probs(p_hat)
    return float(np.mean((p - y) ** 2))


def log_loss_binary(y_true: np.ndarray, p_hat: np.ndarray, eps: float = 1e-6) -> float:
    y = y_true.astype(np.float64)
    p = clip_probs(p_hat, eps)
    return float(-np.mean(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)))


def expected_calibration_error(y_true: np.ndarray, p_hat: np.ndarray, n_bins: int = 10) -> float:
    """Average |confidence - accuracy| weighted by bin mass."""
    y = y_true.astype(np.float64)
    p = clip_probs(p_hat)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    n = len(y)
    if n == 0:
        return 0.0
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        if i == n_bins - 1:
            m = (p >= lo) & (p <= hi)
        else:
            m = (p >= lo) & (p < hi)
        mass = float(np.mean(m))
        if mass == 0.0:
            continue
        conf = float(np.mean(p[m]))
        acc = float(np.mean(y[m]))
        ece += mass * abs(conf - acc)
    return float(ece)


def sharpness(p_hat: np.ndarray) -> float:
    """Mean variance of Bernoulli with pred prob (diagnostic only)."""
    p = clip_probs(p_hat)
    return float(np.mean(p * (1.0 - p)))
