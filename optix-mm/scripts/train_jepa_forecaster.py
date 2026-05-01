"""Train the sklearn JEPA-Forecaster v1 prototype and optionally register if gates pass."""

from __future__ import annotations

from pathlib import Path

import click

from optix.config import reset_settings
from optix.research.jepa_forecaster.train import train_and_maybe_register


@click.command()
@click.option(
    "--register/--no-register",
    default=False,
    help="If gates pass, copy manifest + model into runs/jepa-artifacts/<id>/.",
)
@click.option(
    "--encoder-extra-dim",
    default=0,
    type=int,
    show_default=True,
    help="Trailing zeros for future multimodal embeddings (must match eval/backtest).",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Directory for metrics JSON + joblib (default: $OPTIX_LOG_DIR/jepa-train).",
)
def main(register: bool, encoder_extra_dim: int, output_dir: Path | None) -> None:
    reset_settings()
    manifest, model_path = train_and_maybe_register(
        encoder_extra_dim=encoder_extra_dim,
        register=register,
        output_dir=output_dir,
    )
    click.echo(f"artifact_id={manifest.artifact_id}")
    click.echo(f"gate_passed={manifest.gate.passed if manifest.gate else False}")
    click.echo(f"approved={manifest.approved}")
    click.echo(f"model_path={model_path}")
    if register and manifest.approved:
        click.echo("Registered under runs/jepa-artifacts/ (forecaster.joblib + manifest.json).")


if __name__ == "__main__":
    main()
