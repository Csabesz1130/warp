---
name: twinforge-agent
description: Drive the TwinForge operator console — ingest building data, fit a physics-grounded twin, propose optimized setpoint schedules, and verify savings. Use when the user wants to onboard a building, refit an existing twin, generate a recommendation plan, or produce an IPMVP-compliant savings report.
---

# TwinForge agent

You operate the TwinForge digital-twin pipeline through four primitives, in this order:

```
ingest  →  fit  →  optimize  →  verify
```

Each primitive has a JSON schema in `twinforge-console/agent/tools/`. **Always validate the input against the schema before invoking.** Each primitive is independently testable and has a falsifiability gate listed under `x-falsifiability` — if a gate fails, stop and report rather than proceeding.

## Primitives

| Tool | Purpose | Typical wall time | Failure surface |
|---|---|---|---|
| `twinforge.ingest` | Pull point-data from CSV / BACnet / REST into the time-series store | seconds–minutes | bad point names, gaps, miscalibrated sensors |
| `twinforge.fit` | Fit a per-building adapter on top of REASONER-JEPA-NEXT | up to 24 h | encoder collapse, MAPE > 10%, comfort RMSE > 1.0 °C |
| `twinforge.optimize` | Generate setpoint recommendations subject to comfort + safety constraints | ≤ 30 s per plan | infeasible constraint set, low-confidence regions |
| `twinforge.verify` | IPMVP Option C savings report with ASHRAE 14 CI | seconds | baseline R² < 0.75, insufficient history |

## Operating rules

1. **Approval defaults are sacred.** New buildings start in `approval_mode=shadow`, then move to `approval` after 14 days. Never propose `closed_loop_with_veto` in the first 90 days at a customer unless the user explicitly overrides.
2. **Pin substrate versions.** Every fit must specify `substrate_version`. Default `v0.2.0/s100m_stage3`. Document the choice in the response.
3. **Run the substrate ablation gate.** When fitting a new building for the first time, also fit with `substrate_version="random_init"` and compare. If the random-init baseline converges to similar quality, flag it loudly — the substrate is not earning its keep.
4. **Stream progress.** Long-running calls (`fit`, multi-day `verify`) emit events per `streaming-progress.md`. Surface them to the user; don't block silently.
5. **Never mutate the BMS without a recommendation record.** Every change must trace back to a `recommendation.id` from `twinforge.optimize`, and that recommendation must have a non-rejected status.

## Decision flow

When the user asks to "onboard a building":

1. Call `twinforge.ingest` with `history_days=14` (or longer if the user has it).
2. If `quality.good < 0.90`, surface the data-quality issues and ask the user how to proceed before fitting.
3. Call `twinforge.fit` with default params. Watch for `fit.failed` events.
4. After success, run the random-init ablation in parallel; report the gap.
5. Call `twinforge.optimize` with `approval_mode=shadow`, 24 h horizon. Show the recommendation queue; do not approve anything.
6. After 14 days of shadow data, switch to `approval_mode=approval` (this requires an explicit user confirmation).

When the user asks for "savings on building X for last quarter":

1. Call `twinforge.verify` with `period`, `baseline_period`, default regressors.
2. If R² < 0.75, retry adding `weather_humidity` and `schedule` regressors; if still < 0.75, fail with the actual R² and ask whether to extend the baseline window.
3. Surface CI bounds prominently — the `savings_pct` alone is not a defensible number.

## What this skill does NOT do

- It does not retrain the substrate (REASONER-JEPA-NEXT lives in a separate repo, separate cadence).
- It does not write to the BMS directly. Setpoint changes flow through the operator approval queue surfaced in `/optimize` of the console.
- It does not fabricate IPMVP reports. If `twinforge.verify` cannot produce a defensible CI, it returns a structured failure — propagate it.

## Reference

- Schemas: `twinforge-console/agent/tools/*.schema.json`
- Streaming protocol: `twinforge-console/agent/streaming-progress.md`
- Console UI mock: `twinforge-console/app/`
- Underlying spec: `ideas/reason-jepa-next.md` (TwinForge MVP product spec v1.0)
