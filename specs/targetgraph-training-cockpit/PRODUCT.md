# TargetGraph Training Cockpit

## Summary

Warp provides a terminal-native operator cockpit for TargetGraph JEPA pretraining, NYX automation, campaign status inspection, and adapter promotion. Warp remains the orchestration surface while TargetGraph remains the training runtime and source of model truth.

## Problem

TargetGraph already has training scripts, JEPA domains, flywheel scoring, and promotion concepts, but operators need a repeatable terminal workflow that can be run manually, by Warp workflows, or by an agent inside Warp without copying TargetGraph internals into the Warp repository.

## Goals

1. Let a Warp user run common TargetGraph training operations from a local Warp checkout.
2. Keep the integration thin: no vendoring TargetGraph code and no model-training logic inside Warp.
3. Make every operation suitable for Warp workflows and agent execution by requiring deterministic commands and JSON-friendly output.
4. Fail fast with actionable setup guidance when the TargetGraph checkout or CLI is unavailable.

## Non-goals

1. Warp does not train models directly.
2. Warp does not own TargetGraph data lake, model registry, Modal jobs, Redis queues, or adapter artifacts.
3. Warp does not define biomedical training quality thresholds; it only calls TargetGraph commands that enforce those gates.

## Behavior

1. A user can run `integrations/targetgraph/tg-warp doctor` from the Warp repository to verify the TargetGraph bridge setup.

2. The doctor command reports which TargetGraph CLI path will be used and which TargetGraph repo path is configured or discovered.

3. The bridge resolves the TargetGraph CLI in this order: explicit `TARGETGRAPH_CLI`, virtualenv executable under `TARGETGRAPH_REPO`, Python fallback script under `TARGETGRAPH_REPO`, and finally `tg` from `PATH`.

4. If no TargetGraph CLI can be resolved, the bridge exits non-zero and tells the user to set `TARGETGRAPH_REPO` or `TARGETGRAPH_CLI`.

5. A user can run a JEPA cold-start job from Warp with `tg-warp coldstart --domain <domain|all> --profile <minimal|standard|full>`.

6. A user can run NYX automation from Warp with `tg-warp nyx --profile <minimal|standard|full>`.

7. A user can inspect campaign status from Warp with `tg-warp status --campaign <campaign>`.

8. A user can promote an adapter from Warp with `tg-warp promote --campaign <campaign> --adapter <adapter>`.

9. Adapter promotion requires TargetGraph pass gates by default. Users must explicitly pass `--no-require-pass` to omit the gate flag.

10. Every first-class bridge command forwards to `tg train ... --json` so Warp workflows and agents can parse the result.

11. The bridge supports `tg-warp passthrough -- <args>` so new TargetGraph training subcommands can be used before Warp adds dedicated wrappers.

12. Warp workflow files exist for common operations: JEPA cold start, NYX overnight automation, campaign status, and adapter promotion.

13. Workflow arguments expose only the minimal operator inputs needed for the flow: domain, profile, campaign, and adapter.

14. The integration README explains local setup, command examples, CLI resolution order, and the expected TargetGraph command contract.

15. The bridge must remain safe to run in a fork without a TargetGraph checkout. Missing dependencies produce an error; they do not mutate the Warp repo or attempt to install packages automatically.
