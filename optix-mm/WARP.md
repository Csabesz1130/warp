# Optix-MM + Warp

Optix-MM is embedded in the Warp repository so operators can run Kalshi research,
calibration, and paper execution **from the same terminal** they use for Warp
development—optionally alongside TargetGraph/JEPA workflows under
`integrations/targetgraph/`.

Workflow commands assume a recent `uv` with `sync` and `run`. If those subcommands are missing, open the workflow YAML under `.warp/workflows/`, replace the `cd optix-mm && uv …` prefix with activating `optix-mm/.venv` and `pip install -e ".[dev]"` / `python -m pytest` as in the main README.

## Workflows

From Warp’s workflow picker, run:

| Workflow | Purpose |
|----------|---------|
| **Optix-MM: pytest** | `uv sync` + unit tests (no dataset required) |
| **Optix-MM: replicate Becker** | Sanity-check dataset vs Becker (2026) Table 1 |
| **Optix-MM: build calibration** | Regenerate `src/optix/data/calibration.json` |
| **Optix-MM: backtest** | Historical replay; prompts for `--start` / `--end` |
| **Optix-MM: paper trade** | Live WebSocket paper mode; prompts for `--max-markets` |
| **Optix-MM: JEPA train** | Train gated sklearn forecaster on Becker aggregates (`scripts/train_jepa_forecaster.py`) |
| **Optix-MM: JEPA eval** | Holdout gate report for a saved joblib (`scripts/eval_jepa_forecaster.py`) |

Workflow definitions live in the Warp repo root:

- [.warp/workflows/optix-mm-pytest.yaml](../.warp/workflows/optix-mm-pytest.yaml)
- [.warp/workflows/optix-mm-replicate-becker.yaml](../.warp/workflows/optix-mm-replicate-becker.yaml)
- [.warp/workflows/optix-mm-build-calibration.yaml](../.warp/workflows/optix-mm-build-calibration.yaml)
- [.warp/workflows/optix-mm-backtest.yaml](../.warp/workflows/optix-mm-backtest.yaml)
- [.warp/workflows/optix-mm-paper.yaml](../.warp/workflows/optix-mm-paper.yaml)
- [.warp/workflows/optix-mm-jepa-train.yaml](../.warp/workflows/optix-mm-jepa-train.yaml)
- [.warp/workflows/optix-mm-jepa-eval.yaml](../.warp/workflows/optix-mm-jepa-eval.yaml)

## Environment

- Set `BECKER_DATA_DIR` to your Becker Parquet tree (see main README).
- For paper/live feed: copy `.env.example` to `optix-mm/.env` and add Kalshi credentials.
- For hybrid / forecast ablation: set `OPTIX_FORECAST_MODE` and `OPTIX_FORECAST_ARTIFACT_ID`
  after an artifact passes gates and is copied into `runs/jepa-artifacts/<id>/`.

## Agents

Natural-language ops map cleanly to the same commands the workflows run, for example:
“Run Optix backtest from 2025-01-01 to 2025-11-25” →
`cd optix-mm && uv run python scripts/run_backtest.py --start 2025-01-01 --end 2025-11-25`.

Keep **JSON or structured logs** in `runs/` if you want agents to summarize paper sessions.
