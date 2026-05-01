"""Run OptimismTax-MM in paper-trading mode against the live Kalshi feed."""

from __future__ import annotations

import asyncio
import logging
import sys

import click
import structlog

from optix.execution.live_runner import run


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )


@click.command()
@click.option("--max-markets", default=200, type=int, help="Max markets to subscribe.")
def main(max_markets: int) -> None:
    configure_logging()
    asyncio.run(run(max_markets=max_markets))


if __name__ == "__main__":
    main()
