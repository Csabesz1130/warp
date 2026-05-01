"""Run the OptimismTax-MM backtest against Becker's dataset."""

from __future__ import annotations

import os

import click
from rich.console import Console
from rich.table import Table

from optix.config import reset_settings
from optix.strategy.backtest import run_backtest, save_result


@click.command()
@click.option("--start", default=None, help="ISO date e.g. 2025-01-01")
@click.option("--end", default=None, help="ISO date e.g. 2025-11-25")
@click.option(
    "--forecast-mode",
    default=None,
    type=click.Choice(["structural_only", "hybrid", "forecast_ablation"]),
    help="Override OPTIX_FORECAST_MODE for this run (resets cached settings).",
)
@click.option(
    "--forecast-artifact-id",
    default=None,
    help="Override OPTIX_FORECAST_ARTIFACT_ID (registered runs/jepa-artifacts/<id>/forecaster.joblib).",
)
def main(
    start: str | None,
    end: str | None,
    forecast_mode: str | None,
    forecast_artifact_id: str | None,
) -> None:
    if forecast_mode is not None:
        os.environ["OPTIX_FORECAST_MODE"] = forecast_mode
    if forecast_artifact_id is not None:
        os.environ["OPTIX_FORECAST_ARTIFACT_ID"] = forecast_artifact_id
    reset_settings()

    console = Console()
    result = run_backtest(start=start, end=end)
    path = save_result(result)

    t = Table(title="OptimismTax-MM backtest summary")
    t.add_column("Metric")
    t.add_column("Value", justify="right")
    t.add_row("Fills", f"{result.n_fills:,}")
    t.add_row("Markets with positions", f"{result.n_markets_with_position:,}")
    t.add_row("Capital deployed", f"${result.capital_deployed_usd:,.2f}")
    t.add_row("Realized PnL", f"${result.realized_pnl_usd:+,.2f}")
    t.add_row("Forecast mode", result.forecast_mode)
    t.add_row("Forecast artifact", result.forecast_artifact_id or "(none)")
    t.add_row("Forecaster loaded", "yes" if result.forecaster_loaded else "no")
    if result.capital_deployed_usd > 0:
        roi = 100.0 * result.realized_pnl_usd / result.capital_deployed_usd
        t.add_row("ROI on capital", f"{roi:+.2f}%")
    console.print(t)

    if result.per_category:
        ct = Table(title="Per-category breakdown")
        for col in ["category", "capital_usd", "pnl_usd", "roi_pct"]:
            ct.add_column(col, justify="right")
        for cat, row in sorted(
            result.per_category.items(), key=lambda kv: -kv[1]["realized_pnl_usd"]
        ):
            ct.add_row(
                cat,
                f"${row['capital_usd']:,.2f}",
                f"${row['realized_pnl_usd']:+,.2f}",
                f"{row['roi_pct']:+.3f}%",
            )
        console.print(ct)

    console.print(f"\nFull report: {path}")


if __name__ == "__main__":
    main()
