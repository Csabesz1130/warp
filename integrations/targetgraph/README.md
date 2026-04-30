# TargetGraph + Warp integration

This integration keeps Warp as the operator cockpit and leaves TargetGraph as the training runtime. It does not vendor TargetGraph code into Warp and does not make Warp responsible for model training. Instead, Warp workflows call a stable `tg train` command exposed by a local TargetGraph checkout.

## Local setup

```bash
export TARGETGRAPH_REPO=/path/to/targetgraph_research_suite
export TARGETGRAPH_PROFILE=minimal
integrations/targetgraph/tg-warp doctor
```

The bridge resolves `tg` in this order:

1. `$TARGETGRAPH_CLI`, when set.
2. `$TARGETGRAPH_REPO/.venv/bin/tg`, when present.
3. `$TARGETGRAPH_REPO/scripts/targetgraph_train_cli.py`, as a Python module-style fallback.
4. `tg` from `$PATH`.

## Operator flows

```bash
integrations/targetgraph/tg-warp coldstart --domain graph --profile minimal
integrations/targetgraph/tg-warp nyx --profile standard
integrations/targetgraph/tg-warp status --campaign catsper
integrations/targetgraph/tg-warp promote --campaign catsper --adapter catsper_v3
```

Each command forwards to `tg train ...` and is designed to be used from Warp workflows, Warp agent sessions, or any external CLI agent running inside Warp.

## Contract expected from TargetGraph

TargetGraph should expose these commands with JSON-friendly output:

```bash
tg train doctor --json
tg train coldstart --domain <domain|all> --profile <minimal|standard|full> --json
tg train nyx --profile <minimal|standard|full> --json
tg train status --campaign <campaign> --json
tg train promote --campaign <campaign> --adapter <adapter> --require-pass --json
```

The bridge intentionally fails fast when no TargetGraph checkout or CLI is available so Warp remains a thin orchestration layer.
