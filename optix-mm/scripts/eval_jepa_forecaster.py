"""Evaluate a saved forecaster joblib on the holdout split; print or write gate summary JSON."""

from __future__ import annotations

import json
from pathlib import Path

import click

from optix.config import reset_settings
from optix.research.jepa_forecaster.eval_report import evaluate_joblib, evaluate_joblib_to_json


@click.command()
@click.argument(
    "model_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
)
@click.option(
    "--out-json",
    type=click.Path(path_type=Path),
    default=None,
    help="Write full report JSON to this path (default: print to stdout).",
)
def main(model_path: Path, out_json: Path | None) -> None:
    reset_settings()
    if out_json is not None:
        evaluate_joblib_to_json(model_path, out_json)
        click.echo(str(out_json))
    else:
        report = evaluate_joblib(model_path)
        click.echo(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
