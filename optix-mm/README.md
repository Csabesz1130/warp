# OptimismTax-MM

A market-making strategy for Kalshi prediction markets that captures the
"Optimism Tax" — the structural wealth transfer from liquidity-taking
retail (who buy YES at longshot prices) to liquidity-providing makers
(who sell NO into that biased flow).

The edge is documented in Becker (2026), *The Microstructure of Wealth
Transfer in Prediction Markets*, and quantified across 72.1M trades and
$18.26B of volume:

| Category | Maker–Taker Gap (pp) |
|---|---|
| World Events | 7.32 |
| Media | 7.28 |
| Entertainment | 4.79 |
| Crypto | 2.69 |
| Weather | 2.57 |
| Sports | 2.23 |
| Politics | 1.02 |
| Finance | 0.17 (avoid) |

Strategy v0 trades only the high-engagement categories and ignores
Finance entirely.

## Mechanism

For binary contracts in `{Sports, Entertainment, Media, World Events,
Crypto, Weather}` where YES is trading 1–15¢ (longshot regime), and
recent trade tape is biased toward YES-buying takers, post resting NO
bids one tick below the best NO offer. When taker YES-buy flow hits
the book, our resting NO orders fill at the matching NO price.

Hold to resolution. ~96% of 5¢ YES contracts expire worthless, paying
the NO holder $1. EV per contract at YES=5¢: roughly +1¢, or +1% on
capital risked over the holding period.

## Layout

    src/optix/
      data/        - Becker dataset loader (DuckDB over Parquet)
      research/    - replicate Becker's findings, fit category gaps,
                     calibrate longshot premium
      strategy/    - signal computation, position sizing, backtester
      kalshi/      - REST + WebSocket clients with RSA-PSS auth
      execution/   - paper trader + live runner (paper-only by default)
      risk/        - position caps, daily drawdown halt, kill switch
      monitoring/  - PnL tracking, Brier diagnostics

## Setup

Requires Python 3.11+ and `uv` (https://github.com/astral-sh/uv).

    uv venv
    uv sync

Pull Becker's dataset (~33 GB compressed). Easiest path is to clone his
repo and use his downloader:

    git clone https://github.com/Jon-Becker/prediction-market-analysis
    cd prediction-market-analysis
    uv sync
    python main.py    # interactive menu, choose "Download data"
    cd ..

Then point optix at the extracted Parquet directory:

    export BECKER_DATA_DIR="$PWD/prediction-market-analysis/data"

Get Kalshi API credentials at https://kalshi.com/account/profile and
write the private key to `secrets/kalshi.pem`. Copy `.env.example` to
`.env` and fill in `KALSHI_KEY_ID`.

## Run

Sanity check: replicate Table 1 of Becker (2026):

    uv run python scripts/replicate_becker.py

Backtest the strategy against Becker's resolved markets:

    uv run python scripts/run_backtest.py --start 2025-01-01 --end 2025-11-25

Hybrid backtest with an approved JEPA-Forecaster artifact (loads
`runs/jepa-artifacts/<id>/forecaster.joblib` when gates passed at train time):

    export OPTIX_FORECAST_MODE=hybrid
    export OPTIX_FORECAST_ARTIFACT_ID=<artifact_id_from_manifest>
    uv run python scripts/run_backtest.py --start 2025-01-01 --end 2025-11-25

Train / evaluate the v1 prototype (sklearn MLP + strict Brier/log-loss/ECE gates vs
implied YES-price baseline):

    uv run python scripts/train_jepa_forecaster.py
    uv run python scripts/eval_jepa_forecaster.py ./runs/jepa-train/forecaster-<id>.joblib --out-json ./runs/jepa-eval.json

Paper-trade live (no real orders, no real money):

    uv run python scripts/run_paper.py

The paper runner connects to Kalshi's WebSocket, simulates posting NO
bids on qualifying markets, and logs simulated fills + PnL to
`runs/paper-{date}.jsonl`.

## Going live

When you're satisfied with paper-trading metrics:

1. Set `OPTIX_LIVE=1` and `OPTIX_BANKROLL_USD=<starting capital>` in `.env`.
2. Lower the per-market position cap in `risk/limits.py` (default is
   conservative).
3. Run `uv run python scripts/run_paper.py --live`.

A daily 4% drawdown trips the kill switch and flattens. Manual restart
is required.

## What's not in v0

- Polymarket connector (post-MVP — Becker's edge is documented on
  Kalshi specifically; Polymarket microstructure is a separate paper).
- **JEPA-Forecaster v1** is available as an additive, gated subsystem under
  `src/optix/research/jepa_forecaster/` (sklearn encoder-head prototype today;
  swap for a multimodal JEPA encoder later). Artifacts only register when
  holdout metrics beat the implied-price baseline by configured margins and ECE
  is within tolerance—otherwise training stays fail-closed.
- INTEGRA surveillance integration.
- Multi-venue smart order routing.

These are the next layers, not v0.

## Warp monorepo

When checked out inside the Warp repo, you can run **Optix-MM** from Warp workflows; see [WARP.md](WARP.md) and [integrations/optix-mm/README.md](../integrations/optix-mm/README.md).
