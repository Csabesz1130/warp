# TwinForge streaming-progress protocol

Long-running TwinForge calls emit a stream of newline-delimited JSON events
(NDJSON) over the same HTTP response, so an agent or operator can follow
progress without polling. This document defines the event envelope and the
per-tool event vocabulary.

## Envelope

Every event is a single JSON object on its own line:

```json
{"v":1,"tool":"twinforge.fit","run_id":"r_abc123","ts":"2026-05-01T12:00:00Z","kind":"fit.epoch","data":{...}}
```

| Field | Type | Description |
|---|---|---|
| `v` | integer | Protocol version. Currently `1`. |
| `tool` | string | Fully-qualified tool name. |
| `run_id` | string | Stable across all events for a single invocation. |
| `ts` | RFC 3339 timestamp | UTC. |
| `kind` | string | Event kind from the per-tool table below. |
| `data` | object | Kind-specific payload. |
| `level` | `"info"`\|`"warn"`\|`"error"` | Optional. Default `"info"`. |

Consumers should ignore unknown fields and unknown `kind` values (forward
compatibility).

## Lifecycle rules

1. The first event for a run is always `<tool>.started`.
2. The last event is always one of `<tool>.completed` or `<tool>.failed`.
3. Between them, intermediate events are best-effort; the absence of an
   intermediate event is not an error.
4. After `<tool>.completed` or `<tool>.failed`, no further events are emitted
   for that `run_id`.
5. If the connection drops, the consumer should treat the run as `unknown`
   and call the corresponding `status` endpoint with the `run_id`.

## Per-tool event vocabulary

### `twinforge.ingest`

| `kind` | `data` |
|---|---|
| `ingest.started` | `{ "building_id": str, "source_kind": "csv"\|"bacnet"\|"rest" }` |
| `ingest.points_discovered` | `{ "n": int }` |
| `ingest.classified` | `{ "n_classified": int, "n_total": int, "accuracy_estimate": float }` |
| `ingest.quality` | `{ "good": float, "stale": float, "interpolated": float, "invalid": float }` |
| `ingest.completed` | full `x-output` of `ingest.schema.json` |
| `ingest.failed` | `{ "reason": str, "retryable": bool }` |

### `twinforge.fit`

| `kind` | `data` |
|---|---|
| `fit.started` | `{ "building_id": str, "substrate_version": str, "history_window_days": int }` |
| `fit.epoch` | `{ "epoch": int, "loss": float, "lr": float, "wall_seconds": float }` |
| `fit.refit` | `{ "layer": str, "delta_loss": float }` |
| `fit.validation` | `{ "energy_mape_7d": float, "zone_temp_rmse_24h_c": float, "calibration_ece": float }` |
| `fit.gate_check` | `{ "gate": str, "passed": bool, "value": float, "threshold": float }` |
| `fit.completed` | full `x-output` of `fit.schema.json` |
| `fit.failed` | `{ "reason": str, "stage": "load"\|"adapter"\|"validation"\|"ablation" }` |

### `twinforge.optimize`

| `kind` | `data` |
|---|---|
| `optimize.started` | `{ "building_id": str, "horizon_hours": int, "approval_mode": str }` |
| `optimize.candidate_proposed` | `{ "candidate_id": str, "predicted_savings_pct": float, "confidence": float }` |
| `optimize.refinement_step` | `{ "step": int, "delta_energy_kwh": float, "comfort_ok": bool }` |
| `optimize.fallback_engaged` | `{ "reason": "low_confidence"\|"infeasible"\|"timeout", "fallback": "casadi_mpc" }` |
| `optimize.completed` | full `x-output` of `optimize.schema.json` |
| `optimize.failed` | `{ "reason": str }` |

### `twinforge.verify`

| `kind` | `data` |
|---|---|
| `verify.started` | `{ "building_id": str, "period": str }` |
| `verify.baseline_fit` | `{ "r_squared": float, "regressors": [str] }` |
| `verify.confidence_interval` | `{ "method": "ASHRAE_14", "level": float, "ci_low_pct": float, "ci_high_pct": float }` |
| `verify.report_generated` | `{ "format": "json"\|"pdf", "url": str }` |
| `verify.completed` | full `x-output` of `verify.schema.json` |
| `verify.failed` | `{ "reason": "baseline_r2_below_threshold"\|"insufficient_history"\|"meter_gap", "details": object }` |

## Worked example

A single `twinforge.fit` invocation over 5 minutes (truncated):

```json
{"v":1,"tool":"twinforge.fit","run_id":"r_9af","ts":"2026-05-01T12:00:00Z","kind":"fit.started","data":{"building_id":"lbnl_b59","substrate_version":"v0.2.0/s100m_stage3","history_window_days":14}}
{"v":1,"tool":"twinforge.fit","run_id":"r_9af","ts":"2026-05-01T12:00:31Z","kind":"fit.epoch","data":{"epoch":1,"loss":0.412,"lr":0.001,"wall_seconds":31}}
{"v":1,"tool":"twinforge.fit","run_id":"r_9af","ts":"2026-05-01T12:01:02Z","kind":"fit.epoch","data":{"epoch":2,"loss":0.318,"lr":0.001,"wall_seconds":62}}
{"v":1,"tool":"twinforge.fit","run_id":"r_9af","ts":"2026-05-01T12:04:11Z","kind":"fit.validation","data":{"energy_mape_7d":0.068,"zone_temp_rmse_24h_c":0.42,"calibration_ece":0.031}}
{"v":1,"tool":"twinforge.fit","run_id":"r_9af","ts":"2026-05-01T12:04:11Z","kind":"fit.gate_check","data":{"gate":"energy_mape_7d","passed":true,"value":0.068,"threshold":0.10}}
{"v":1,"tool":"twinforge.fit","run_id":"r_9af","ts":"2026-05-01T12:04:13Z","kind":"fit.completed","data":{"building_id":"lbnl_b59","adapter_path":"adapters/lbnl_b59_v3.pt","substrate_version":"v0.2.0/s100m_stage3","fit_seconds":253,"validation":{"energy_mape_7d":0.068,"zone_temp_rmse_24h_c":0.42,"calibration_ece":0.031},"passed_falsifiability_gate":true}}
```

## Transports

The protocol is transport-agnostic. Recommended bindings:

- **HTTP:** `Content-Type: application/x-ndjson`, chunked transfer encoding,
  one event per line.
- **WebSocket:** one JSON message per event.
- **stdout (CLI):** one event per line, `flush()` after each.
