# Setup directions (brainstorm follow-through)

This document captures decisions and backlog from the Warp + TargetGraph/JEPA brainstorm. It does not change runtime behavior; see [README.md](README.md) for setup and operator commands.

## Primary track: orchestration-first (with optional hybrid)

**Chosen default: TargetGraph orchestration** — extend `tg-warp`, [.warp/workflows](../../.warp/workflows/), and operator docs so Warp remains a thin cockpit over TargetGraph’s training runtime.

**Rationale:** The repo already encodes this split in [specs/targetgraph-training-cockpit/PRODUCT.md](../../specs/targetgraph-training-cockpit/PRODUCT.md) (Warp does not train models; JSON-stable CLI for workflows and agents).

**Hybrid note:** On-device ONNX work ([crates/input_classifier](../../crates/input_classifier/)) is a separate product track (shell vs AI routing, future small classifiers). It does not replace TG/JEPA training; teams can pursue both without merging training into Warp.

---

## TargetGraph CLI contract (confirmed)

The bridge script [tg-warp](tg-warp) resolves `tg` per [README.md](README.md), then invokes **`tg train <subcommand> …`** (or `python …/targetgraph_train_cli.py train …`). First-class `tg-warp` commands append **`--json`** so workflows and agents can parse stdout.

| `tg-warp` command | Forwarded `tg train` invocation |
|-------------------|--------------------------------|
| `doctor` | `train doctor --json` |
| `coldstart` | `train coldstart --domain <domain\|all> --profile <minimal\|standard\|full> --json` |
| `nyx` | `train nyx --profile <minimal\|standard\|full> --json` |
| `status` | `train status --campaign <campaign> --json` |
| `promote` | `train promote --campaign <campaign> --adapter <adapter> [--require-pass] --json` (omit `--require-pass` when using `--no-require-pass`) |
| `passthrough -- …` | `train <args…>` — **no automatic `--json`**; caller supplies flags |

**TargetGraph’s responsibility:** Implement `tg train` subcommands so successful runs emit machine-readable JSON on stdout as documented in README; fail fast with non-zero exit on errors.

**Subcommands wrapped by `tg-warp` today:** `doctor`, `coldstart`, `nyx`, `status`, `promote`.

**Extension path:** New TG subcommands ship behind `tg-warp passthrough -- <args>` until stable enough to add a dedicated wrapper (mirrors [specs/targetgraph-training-cockpit/PRODUCT.md](../../specs/targetgraph-training-cockpit/PRODUCT.md) behavior 11).

---

## Workflow backlog (recurring jobs → `.warp/workflows`)

Existing workflows: `targetgraph-jepa-coldstart.yaml`, `targetgraph-nyx-overnight.yaml`, `targetgraph-campaign-status.yaml`, `targetgraph-promote-adapter.yaml`.

Candidates to add when TG exposes matching `tg train` surfaces or via `passthrough`:

1. **Eval sweep** — parameterized domain/profile/grid; sequential or parallel invocations; aggregate JSON (jq/script).
2. **Ablation / architecture A–B** — fixed harness calling `passthrough` with experiment-specific args; same aggregation pattern.
3. **Checkpoint smoke test** — short run or load-check after checkpoint write; gates “good enough to kick NYX”.
4. **Resume-from-step** — wraps TG resume semantics once CLI supports it.
5. **Benchmark harness** — N configs, collect JSON, tabular summary for humans or agents.
6. **Flywheel / scoring visibility** — format TG metrics JSON into terminal-friendly output.
7. **Pre-flight extended doctor** — optional second step (env GPU, Modal auth, disk) **outside** `tg`; can stay a separate script or workflow step.
8. **Run metadata sidecar** — workflow step appending run id, Warp/TG git SHA, and CLI args to a local JSONL for reproducibility.

Prioritize by what TargetGraph stabilizes on `tg train … --json` first; use `passthrough` until then.
