# Optix-MM (Warp monorepo)

[Optix-MM](../../optix-mm/) is a Kalshi market-making research stack (Becker dataset,
signals, backtest, paper trading). It lives beside Warp so you can drive the same
terminal workflows as **TargetGraph** (`integrations/targetgraph/tg-warp`) without
mixing Python environments.

- **Code & docs:** [optix-mm/README.md](../../optix-mm/README.md)
- **Warp entrypoints:** [optix-mm/WARP.md](../../optix-mm/WARP.md)
- **Workflows:** `.warp/workflows/optix-mm-*.yaml` (search “Optix-MM” in the workflow picker)

Typical order: pytest workflow → download Becker data → replicate → build calibration → backtest → paper.
Optional: JEPA-Forecaster train/eval workflows (`optix-mm-jepa-train`, `optix-mm-jepa-eval`) before enabling hybrid mode via env vars (see `optix-mm/.env.example`).
