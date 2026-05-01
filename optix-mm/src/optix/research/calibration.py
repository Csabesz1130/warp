"""Empirical YES winrate by category and price level, computed from Becker.

The signals module needs a `historical_yes_winrate` to compute expected
value. Becker's main finding is that this winrate is structurally *below*
the implied probability (the YES price) at longshot prices. We compute
it once per category from his dataset and cache the result.

Run `uv run python scripts/build_calibration.py` to regenerate.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from optix.data.becker_loader import BeckerDataPaths, connect, trades_with_outcomes
from optix.data.categories import category_for_event_ticker

CALIBRATION_PATH = Path(__file__).parent.parent / "data" / "calibration.json"


@dataclass
class CalibrationKey:
    category: str
    yes_price_cents: int


def calibrate(min_obs_per_cell: int = 200) -> dict[str, dict[int, float]]:
    """Compute YES winrate per (category, yes_price_cents) cell.

    Returns:
        {category: {yes_price_cents: winrate_0_to_1}}
    """
    paths = BeckerDataPaths.from_settings()
    con = connect()
    trades = trades_with_outcomes(con, paths, price_lo=1, price_hi=99, min_market_volume=100)

    # Map each trade to a category via its event_ticker prefix
    trades = trades.with_columns([
        pl.col("event_ticker")
          .map_elements(category_for_event_ticker, return_dtype=pl.Utf8)
          .alias("category"),
        (pl.col("result") == "yes").cast(pl.Int8).alias("yes_won"),
    ])

    grouped = (
        trades.group_by(["category", "yes_price"])
        .agg([
            pl.len().alias("n"),
            pl.col("yes_won").mean().alias("yes_winrate"),
        ])
        .filter(pl.col("n") >= min_obs_per_cell)
        .sort(["category", "yes_price"])
    )

    out: dict[str, dict[int, float]] = {}
    for row in grouped.iter_rows(named=True):
        out.setdefault(row["category"], {})[int(row["yes_price"])] = float(row["yes_winrate"])
    return out


def save_calibration(table: dict[str, dict[int, float]]) -> None:
    CALIBRATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    serializable = {cat: {str(p): w for p, w in cells.items()} for cat, cells in table.items()}
    CALIBRATION_PATH.write_text(json.dumps(serializable, indent=2))


def load_calibration() -> dict[str, dict[int, float]]:
    if not CALIBRATION_PATH.exists():
        return {}
    raw = json.loads(CALIBRATION_PATH.read_text())
    return {cat: {int(p): w for p, w in cells.items()} for cat, cells in raw.items()}


def yes_winrate_for(
    category: str,
    yes_price_cents: int,
    table: dict[str, dict[int, float]] | None = None,
) -> float | None:
    """Lookup with sensible fallbacks: nearest price level within 2c, else None."""
    if table is None:
        table = load_calibration()
    cells = table.get(category)
    if not cells:
        return None
    if yes_price_cents in cells:
        return cells[yes_price_cents]
    # Fall back to nearest cent within +/- 2
    for delta in (1, -1, 2, -2):
        p = yes_price_cents + delta
        if p in cells:
            return cells[p]
    return None


if __name__ == "__main__":
    table = calibrate()
    save_calibration(table)
    print(f"Wrote {sum(len(v) for v in table.values())} cells across {len(table)} categories")
    print(f"Path: {CALIBRATION_PATH}")
