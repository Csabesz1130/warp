"""Replicate Becker (2026) Table 1: maker vs taker excess returns by price level.

Run this first. If our numbers don't match Becker's published findings within
a reasonable tolerance, the dataset is mis-loaded or the schema has shifted
and the rest of the strategy is unsafe to deploy.

Expected pattern from Becker (2026):
- Taker average excess return: roughly -1.12%
- Maker average excess return: roughly +1.12%
- Tails (1c contracts): taker mispricing about -57%, maker about +57%
- Takers exhibit negative excess returns at 80 of 99 price levels
"""

from __future__ import annotations

import polars as pl
from rich.console import Console
from rich.table import Table

from optix.data.becker_loader import (
    BeckerDataPaths,
    connect,
    resolved_market_count,
    trade_count,
    trades_with_outcomes,
)


def excess_return_by_role(trades: pl.DataFrame) -> pl.DataFrame:
    """Compute per-trade excess return for taker and maker positions.

    For a trade at YES price p (cents), the taker's payoff (per $1 risked) is:
      (100 * outcome_yes - p) / p   if taker_side == 'yes'
      (100 * outcome_no  - q) / q   if taker_side == 'no'   where q = 100 - p
    The maker takes the opposite side at the complementary price.
    """
    df = trades.with_columns([
        # Outcome flags
        (pl.col("result") == "yes").cast(pl.Int8).alias("y_yes"),
        (pl.col("result") == "no").cast(pl.Int8).alias("y_no"),
    ]).with_columns([
        # Taker's risked price in cents
        pl.when(pl.col("taker_side") == "yes")
          .then(pl.col("yes_price"))
          .otherwise(pl.col("no_price"))
          .alias("taker_price"),
        pl.when(pl.col("taker_side") == "yes")
          .then(pl.col("y_yes"))
          .otherwise(pl.col("y_no"))
          .alias("taker_outcome"),
    ]).with_columns([
        # Maker is the counterparty at the complementary price
        (100 - pl.col("taker_price")).alias("maker_price"),
        (1 - pl.col("taker_outcome")).alias("maker_outcome"),
    ]).with_columns([
        # Excess returns (gross of fees), per $1 of capital risked
        ((100.0 * pl.col("taker_outcome") - pl.col("taker_price")) / pl.col("taker_price"))
            .alias("taker_ret"),
        ((100.0 * pl.col("maker_outcome") - pl.col("maker_price")) / pl.col("maker_price"))
            .alias("maker_ret"),
    ])
    return df


def aggregate_overall(df: pl.DataFrame) -> dict[str, float]:
    return {
        "n_trades": df.height,
        "taker_mean_ret_pct": float(df["taker_ret"].mean()) * 100.0,
        "maker_mean_ret_pct": float(df["maker_ret"].mean()) * 100.0,
        "gap_pp": float(df["maker_ret"].mean() - df["taker_ret"].mean()) * 100.0,
    }


def aggregate_by_price_level(df: pl.DataFrame) -> pl.DataFrame:
    """Average return at each integer cent of taker_price."""
    return (
        df.group_by("taker_price")
          .agg([
              pl.len().alias("n"),
              (pl.col("taker_ret").mean() * 100.0).alias("taker_ret_pct"),
              (pl.col("maker_ret").mean() * 100.0).alias("maker_ret_pct"),
              (pl.col("taker_outcome").mean() * 100.0).alias("taker_winrate_pct"),
          ])
          .sort("taker_price")
    )


def main() -> None:
    console = Console()
    paths = BeckerDataPaths.from_settings()
    con = connect()

    n_markets = resolved_market_count(con, paths)
    n_trades = trade_count(con, paths)
    console.print(f"[bold]Dataset[/]: {n_trades:,} trades across {n_markets:,} resolved markets")

    console.print("[bold]Loading filtered trades...[/]")
    trades = trades_with_outcomes(con, paths, price_lo=1, price_hi=99, min_market_volume=100)
    console.print(f"After filter: {trades.height:,} trades")

    df = excess_return_by_role(trades)
    overall = aggregate_overall(df)

    t = Table(title="Becker (2026) replication — overall returns")
    t.add_column("Metric")
    t.add_column("Value", justify="right")
    t.add_row("Trades analyzed", f"{int(overall['n_trades']):,}")
    t.add_row("Taker mean excess return", f"{overall['taker_mean_ret_pct']:+.2f}%")
    t.add_row("Maker mean excess return", f"{overall['maker_mean_ret_pct']:+.2f}%")
    t.add_row("Gap (maker - taker)", f"{overall['gap_pp']:+.2f} pp")
    console.print(t)

    by_price = aggregate_by_price_level(df)
    tails = by_price.filter(
        (pl.col("taker_price") <= 5) | (pl.col("taker_price") >= 95)
    )

    t2 = Table(title="Tail behaviour (taker_price 1-5 and 95-99 cents)")
    for col in ["taker_price", "n", "taker_ret_pct", "maker_ret_pct", "taker_winrate_pct"]:
        t2.add_column(col, justify="right")
    for row in tails.iter_rows():
        t2.add_row(*[f"{v:,.2f}" if isinstance(v, float) else f"{v}" for v in row])
    console.print(t2)

    # How many price levels show taker losses, per Becker's "80 of 99" finding
    losing_levels = (by_price.filter(pl.col("taker_ret_pct") < 0)).height
    console.print(
        f"[bold]Price levels with negative taker returns:[/] {losing_levels} of {by_price.height} "
        f"(Becker reports ~80 of 99)"
    )


if __name__ == "__main__":
    main()
