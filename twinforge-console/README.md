# TwinForge Operator Console

A Next.js prototype of the TwinForge operator console — the customer-facing UI
for the physics-grounded digital twin product described in
[`ideas/reason-jepa-next.md`](../ideas/reason-jepa-next.md) (TwinForge MVP
spec) and [`ideas/execution-for-reason-jepa.md`](../ideas/execution-for-reason-jepa.md)
(90-day execution plan + pitch deck).

This is a **demo / pitch surface**. All data is mocked. Wire to real ingest /
fit / optimize / verify endpoints later.

## What's here

```
twinforge-console/
├── app/                    # Next.js 14 App Router
│   ├── page.tsx                # Overview
│   ├── twin/page.tsx           # Twin state — zones + equipment
│   ├── optimize/page.tsx       # Recommendation queue + approve/reject
│   ├── verify/page.tsx         # IPMVP Option C savings reports
│   ├── compliance/page.tsx     # NYC LL97 trajectory + fine forecast
│   └── api/                    # Mock JSON endpoints
├── components/             # Sidebar, TopBar, Card/KPI, EnergyChart
├── lib/                    # Types + mock data
└── agent/                  # Agent-driveable layer (not the UI)
    ├── SKILL.md                # twinforge-agent skill description
    ├── streaming-progress.md   # NDJSON event protocol
    └── tools/
        ├── ingest.schema.json
        ├── fit.schema.json
        ├── optimize.schema.json
        └── verify.schema.json
```

## Run it

```bash
cd twinforge-console
npm install
npm run dev      # http://localhost:3030
```

Build / typecheck:

```bash
npm run build
npm run typecheck
```

## Pages

| Page | What it shows |
|---|---|
| `/` Overview | KPIs (today's savings, YTD, comfort violations, pending approvals, twin fit age), 24h energy chart (baseline vs optimized), twin status panel, recent activity feed. |
| `/twin` | Zone tiles (temp, setpoint, occupancy, comfort status) and the equipment inventory table. |
| `/optimize` | Pending recommendation queue with confidence bars; approve/reject actions hit the mock POST endpoint. |
| `/verify` | Quarterly IPMVP Option C savings report with R², CI bounds, and methodology notes. |
| `/compliance` | NYC LL97 emissions trajectory chart and yearly fine forecast (baseline vs optimized). |

## Agent layer

The console doubles as an agent surface. The four primitives that drive the
twin lifecycle are described in `agent/`:

1. **`twinforge.ingest`** — pull point-data into the time-series store
2. **`twinforge.fit`** — fit a per-building adapter on top of REASONER-JEPA-NEXT
3. **`twinforge.optimize`** — generate setpoint recommendations under comfort + safety constraints
4. **`twinforge.verify`** — IPMVP Option C savings report with ASHRAE 14 CI

Each has a JSON Schema (with an `x-output` block defining the success-case
return shape and an `x-falsifiability` block listing the gates a real
implementation must clear). Long-running tools emit NDJSON events per the
streaming-progress spec — see `agent/streaming-progress.md` for the envelope
and per-tool event vocabulary.

The schemas are designed so a Warp agent (or any tool-using LLM) can drive
the full lifecycle without bespoke glue: validate → invoke → stream → store
the result. The console UI is a human render of the same state.

## Mock data

Everything under `lib/mockData.ts`. Building is `LBNL Building 59` (the demo
target named in the MVP spec). Numbers are seeded — they reproduce on every
load so a screen-recorded demo stays stable.

## Not in scope (yet)

- Auth (drop in Clerk or Auth0 when wiring real customers)
- Real BACnet/IP ingest (use the schema; bind to a Python/Go service)
- Real REASONER-JEPA-NEXT inference (separate repo, separate deploy)
- PDF report generation (`/verify` button is a placeholder)
- Operator audit log persistence

These are deliberately deferred per the MVP spec's "narrow, deep, verifiable"
principle.
