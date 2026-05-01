"""Centralized configuration loaded from environment variables and .env file."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Data
    becker_data_dir: Path = Field(default=Path("./prediction-market-analysis/data"))

    # Kalshi
    kalshi_key_id: str = ""
    kalshi_private_key_path: Path = Field(default=Path("./secrets/kalshi.pem"))
    kalshi_api_base: str = "https://api.elections.kalshi.com/trade-api/v2"
    kalshi_ws_url: str = "wss://api.elections.kalshi.com/trade-api/ws/v2"

    # Strategy
    optix_bankroll_usd: float = 10_000.0
    optix_per_market_cap_pct: float = 1.0
    optix_daily_dd_halt_pct: float = 4.0
    optix_target_categories: str = "Sports,Entertainment,Media,WorldEvents,Crypto,Weather"
    optix_longshot_price_lo_cents: int = 1
    optix_longshot_price_hi_cents: int = 15
    optix_taker_imbalance_threshold: float = 0.6
    optix_taker_lookback_trades: int = 20

    # Mode
    optix_live: bool = False

    # Logging
    optix_log_dir: Path = Field(default=Path("./runs"))

    # JEPA-Forecaster v1 (sklearn prototype; gates + registry)
    optix_forecast_mode: Literal["structural_only", "hybrid", "forecast_ablation"] = "structural_only"
    optix_forecast_artifact_id: str = ""
    optix_forecast_hybrid_alpha: float = 0.5
    optix_forecast_encoder_extra_dim: int = 0
    optix_forecast_train_frac: float = 0.70
    optix_forecast_val_frac: float = 0.15
    optix_forecast_gate_brier_delta_min: float = 0.005
    optix_forecast_gate_logloss_delta_min: float = 0.02
    optix_forecast_gate_max_ece: float = 0.12
    optix_forecast_min_test_samples: int = 200
    optix_forecast_min_categories: int = 3
    optix_forecast_ece_bins: int = 10
    optix_forecast_mlp_hidden: str = "64,32"
    optix_forecast_mlp_max_iter: int = 400

    @computed_field
    def forecast_mlp_hidden_tuple(self) -> tuple[int, ...]:
        parts = [p.strip() for p in self.optix_forecast_mlp_hidden.split(",") if p.strip()]
        return tuple(int(x) for x in parts) if parts else (64, 32)

    @property
    def kalshi_markets_dir(self) -> Path:
        return self.becker_data_dir / "kalshi" / "markets"

    @property
    def kalshi_trades_dir(self) -> Path:
        return self.becker_data_dir / "kalshi" / "trades"

    @property
    def target_category_set(self) -> set[str]:
        return {c.strip() for c in self.optix_target_categories.split(",") if c.strip()}


_settings: Settings | None = None


def get_settings() -> Settings:
    """Lazy singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.optix_log_dir.mkdir(parents=True, exist_ok=True)
    return _settings


def reset_settings() -> None:
    """Test helper: clear cached settings."""
    global _settings
    _settings = None
