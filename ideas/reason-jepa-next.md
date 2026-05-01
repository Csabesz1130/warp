# TwinForge MVP — Product Specification v1.0

*The build-bible for the first 90 days of TwinForge engineering. Each subsystem has: (a) what it does, (b) acceptance criteria, (c) integration points with REASONER-JEPA-NEXT, (d) falsifiability gate before progressing.*

---

## Top-level architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        TWINFORGE MVP                                 │
│                                                                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐ │
│  │   INGEST        │ →  │   TWIN          │ →  │   OPTIMIZE      │ │
│  │ (BACnet, MQTT,  │    │ (REASONER-      │    │ (MPC + setpoint │ │
│  │  REST, CSV)     │    │  JEPA-NEXT      │    │  recommendation)│ │
│  └─────────────────┘    │  physics core)  │    └────────┬────────┘ │
│                         └─────────────────┘             │          │
│                                  │                       │          │
│                                  ↓                       ↓          │
│                         ┌─────────────────┐    ┌─────────────────┐ │
│                         │   VERIFY        │    │   DASHBOARD     │ │
│                         │ (savings calc,  │    │ (live state,    │ │
│                         │  IPMVP/M&V)     │    │  recommend,     │ │
│                         └─────────────────┘    │  approve)       │ │
│                                                └─────────────────┘ │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                  ↑
                                  │
                ┌─────────────────┴──────────────────┐
                │   REASONER-JEPA-NEXT SUBSTRATE     │
                │   (separate repo, separate train)  │
                └────────────────────────────────────┘
```

**Five subsystems**: INGEST, TWIN, OPTIMIZE, VERIFY, DASHBOARD. Each is independently testable. Each has a falsifiability gate before the next builds on top of it.

**Substrate boundary:** REASONER-JEPA-NEXT is a *separate repository*, *separate model artifact*, *separate training pipeline*. TwinForge consumes it through a defined API. This separation matters for licensing, for due-diligence (investors can verify the substrate independently), and for the substrate-as-moat narrative.

---

## Subsystem 1 — INGEST

### What it does
Pulls building data from heterogeneous sources into a normalized time-series store.

### Sources (in build order)

1. **CSV / Parquet upload** (week 1 — the demo path; LBNL Building 59, Pecan Street, customer historical exports).
2. **BACnet/IP** (week 5–6 — first real pilot; read-only points: zone temps, setpoints, supply air, valve positions, meter pulses).
3. **MQTT** (week 8+ — for IoT-native buildings).
4. **REST APIs** (week 10+ — for cloud-connected BMS like Schneider EcoStruxure, JCI OpenBlue).
5. **Modbus / proprietary** (post-MVP).

### Normalized schema

```python
@dataclass
class TimeSeriesPoint:
    building_id: str
    point_id: str          # e.g. "AHU-1.SAT", "RM-301.TEMP"
    point_class: str       # one of: zone_temp, setpoint, sat, mat, oat, valve, damper, meter, occupancy
    unit: str              # SI; °C, kW, kWh, m³/h, fraction
    timestamp: datetime    # UTC
    value: float
    quality: int           # 0=good, 1=stale, 2=interpolated, 3=invalid
```

Storage: TimescaleDB or Postgres + TimescaleDB extension. ~50K points × 5-min resolution × 365 days = ~5GB per building per year. Trivial.

### Critical primitives

- **Point-class auto-tagging** — given a BACnet point name, classify it. Use a small classifier (regex + light ML; ~95% accuracy enough for MVP). Manual override in dashboard.
- **Drift detection** — sensors miscalibrate. Flag readings >3σ from rolling-30-day mean as suspect.
- **Gap-filling** — linear interpolation for gaps <60 min, mark as quality=2 (interpolated). Larger gaps mark as missing.
- **Unit normalization** — every value coerced to SI. °F → °C, BTU → J, CFM → m³/h, etc. Store original-unit metadata for round-trip.

### Acceptance test

```python
def test_ingest_lbnl_building59():
    """End-to-end ingest test on the demo dataset."""
    df = load_lbnl_building59("data/lbnl_b59.parquet")
    ingest_result = ingest.upload(df, building_id="lbnl_b59")
    assert ingest_result.points_classified > 0.95 * ingest_result.points_total
    assert ingest_result.quality_distribution["good"] > 0.90
    # Round-trip: read back, recover original (within unit conversion)
    recovered = store.query("lbnl_b59", start, end)
    assert df_equivalent_in_si(df, recovered, atol=1e-3)
```

### Falsifiability gate
- Ingest runs in <60 seconds on 1 year of 5-min-resolution data for one building.
- Auto-tagging accuracy ≥90% on the LBNL benchmark (manually-labeled subset).
- Round-trip test passes.

---

## Subsystem 2 — TWIN

### What it does
Fits a **physics-grounded latent model** to a building's history, then predicts future state given control inputs. This is the part REASONER-JEPA-NEXT directly powers.

### Architecture (two-mode)

**Mode A: Demo / pre-substrate (week 1–4).** A 50–200 state thermal RC network with parameters fit by gradient descent. Conservation laws baked in (thermal balance per zone, airflow continuity). Scipy + Pyomo or JAX-based. Good enough for demo, NOT shipped to customers.

**Mode B: Production / substrate-powered (week 5+).** REASONER-JEPA-NEXT-S100M (then -S1B) fine-tuned on the building's history. Latent state ~512-dim. The substrate provides the *prior* over physical-system dynamics; the building's data provides the *fit*.

### Substrate integration

```python
from reasoner_jepa import (
    HyperbolicEncoder, EncoderConfig,
    HierarchicalThinker, HierarchicalConfig,
    CalibratedStepEnergy, CalibrationConfig,
)
from reasoner_jepa.coconut import langevin_step

class BuildingTwin:
    """Substrate-powered latent twin for one building."""

    def __init__(self, building_id: str, substrate_ckpt: str):
        # Load REASONER-JEPA-NEXT encoder + hierarchical thinker
        self.encoder = HyperbolicEncoder.load(substrate_ckpt + "/encoder.pt")
        self.thinker = HierarchicalThinker.load(substrate_ckpt + "/hierarchical.pt")
        self.energy = CalibratedStepEnergy.load(substrate_ckpt + "/energy.pt")
        # Per-building fine-tune adapter: small MLP that maps building's
        # specific topology (zone graph, equipment list) into the encoder's
        # input space.
        self.adapter = BuildingAdapter(building_id)

    def fit(self, history: TimeSeries, n_epochs: int = 100):
        """24-hour fit pass: adapter parameters tune to this building."""
        # ... gradient descent on adapter only; substrate frozen.

    def predict(
        self, current_state: TimeSeries, control: ControlSchedule, horizon: int
    ) -> Trajectory:
        """Forward the twin under a candidate control; return predicted
        trajectory + per-step energy/uncertainty."""
        # ... run hierarchical thinker; energy head provides confidence.

    def refit(self, recent: TimeSeries):
        """Continuous refit as the building drifts. Lightweight — just
        the adapter + last layer of encoder, never the full substrate."""
```

### Why the substrate matters here
The 24-hour-fit promise is impossible without a strong physics prior. A vanilla RC network with random init takes weeks to fit a building (and badly). REASONER-JEPA-NEXT pretrained on 200B+ tokens of physical-system traces gives the adapter a head start that fits in a single overnight pass. **This is the technical claim that justifies the whole product.**

### Acceptance test

```python
def test_twin_fits_building59_within_24h():
    """Twin fits LBNL Building 59 in under 24 hours of compute."""
    twin = BuildingTwin("lbnl_b59", substrate_ckpt="reasoner_jepa_next_s100m")
    history = load_history("lbnl_b59", days=14)
    t0 = time.time()
    twin.fit(history)
    fit_time = time.time() - t0
    assert fit_time < 24 * 3600  # 24h budget
    
def test_twin_predicts_held_out_week():
    """Twin's 7-day prediction error <10% MAPE on energy."""
    twin = trained_twin("lbnl_b59")
    held_out = load_history("lbnl_b59", days=14, offset_days=14)
    pred = twin.predict(held_out.initial_state, held_out.controls, horizon=7*24*12)
    mape = compute_energy_mape(pred, held_out)
    assert mape < 0.10
```

### Falsifiability gate

- Twin fit completes in ≤24 hours on a single H100 (or equivalent CPU+GPU mix).
- Held-out 7-day energy prediction MAPE ≤10% on three different building datasets (LBNL B59, Pecan Street commercial, one synthetic).
- Comfort-prediction accuracy: zone temp prediction RMSE ≤1.0 °C over 24h horizon.
- **Critical:** Substrate ablation — same fit pipeline with a randomly initialized encoder (no REASONER-JEPA-NEXT pretrain) fails to converge in 24h. This proves the substrate matters. **If the random-init baseline ALSO converges, the substrate isn't earning its keep — investigate.**

---

## Subsystem 3 — OPTIMIZE

### What it does
Given a fitted twin, generate setpoint schedules that minimize energy subject to comfort and safety constraints. Re-plan every 15 minutes over a 24-hour rolling horizon (Model Predictive Control, MPC).

### Optimization formulation

```
minimize:   sum over horizon of predicted_energy(t)
subject to: zone_temp(t) ∈ [setpoint(t) - δ_low, setpoint(t) + δ_high] for all t
            ventilation(t) ≥ ASHRAE 62.1 minimum
            equipment cycling: state changes ≤ N per hour
            ramp rates: |Δ setpoint| ≤ 1°C per 15 min
            occupied hours: setpoints respect schedule
```

**Solver:** Two-stage approach.

1. **Substrate-guided proposal** (cheap, fast): the REASONER-JEPA-NEXT hierarchical thinker proposes K=8 candidate schedules. The energy head scores each. Pick the best.
2. **Refinement via Langevin** (medium cost): take the top candidate, run 5-step Langevin refinement using `langevin_step` from `reasoner_jepa.coconut`, gradient direction = decreasing predicted energy + comfort-constraint penalty.
3. **Optional: classical MPC fallback** (if the substrate is uncertain): fall back to a CasADi/IPOPT classical MPC on the simplified RC network. Costs ~1 second per plan.

The fallback is a safety net for the first 90 days. As the substrate proves itself, fallback is hit less often.

### Operator approval workflow (CRITICAL for early customers)

For the first 90 days at any given customer:
- **Shadow mode (week 1–2):** Twin runs, recommendations log, no setpoint changes.
- **Approval mode (week 3–8):** Operator approves each recommended change before it goes to the BMS. UI shows: predicted savings, comfort risk, confidence interval.
- **Closed-loop with veto (week 9+):** Recommendations auto-apply unless flagged for review. Operator can roll back any change instantly. Daily summary email.

This staging is what makes the buyer trust the product. Do not skip it.

### Acceptance test

```python
def test_optimize_finds_savings_on_b59():
    """Optimization finds ≥10% energy reduction vs baseline on a held-out
    week of LBNL Building 59 in simulation."""
    twin = trained_twin("lbnl_b59")
    week = load_history("lbnl_b59", days=7, offset_days=21)
    baseline_energy = sum_energy(week.observed_controls, twin)
    plan = optimize.plan(twin, week.weather, week.occupancy, horizon=7*24*12)
    optimized_energy = sum_energy(plan.controls, twin)
    savings = (baseline_energy - optimized_energy) / baseline_energy
    assert savings > 0.10
    # Comfort check: predicted zone temps stay in bounds
    pred = twin.predict(week.initial_state, plan.controls, horizon=7*24*12)
    assert (pred.zone_temps >= setpoint - 1.0).all()
    assert (pred.zone_temps <= setpoint + 1.0).all()
```

### Falsifiability gate
- ≥10% predicted savings on held-out LBNL B59, Pecan Street, and one synthetic building, vs baseline (observed) controls.
- Plan generation in ≤30 seconds for a 24h horizon.
- Comfort constraints satisfied 99%+ of the planning horizon.
- **First real customer:** measured savings ≥5% in shadow mode after 30 days. (The simulated 10% target translates to roughly 5–8% in the wild due to model-reality gap.)

---

## Subsystem 4 — VERIFY

### What it does
Compute defensible savings numbers using IPMVP-compliant baselines. This is the slide that makes the customer keep paying.

### Methodology

**IPMVP Option C (Whole Facility):** the standard for HVAC retrofit M&V.

1. **Baseline period:** 12 months of pre-deployment data, ideally; 3 months minimum.
2. **Baseline regression:** energy ~ f(weather, occupancy, time-of-day, day-of-week). Multi-variable regression, R² ≥ 0.75 required.
3. **Adjusted baseline:** apply the regression to the post-deployment weather/occupancy to get expected energy under old controls.
4. **Avoided energy:** adjusted baseline − measured.
5. **Confidence interval:** ASHRAE Guideline 14 statistical CI; report as "X% ± Y% at 90% confidence."

### Outputs

- Monthly **Verified Savings Report** (PDF, customer-facing).
- Annual **M&V Audit Package** (third-party-auditable, IPMVP-compliant).
- LL97 / BERDO / EPBD compliance reporting (jurisdiction-specific formats).

### Acceptance test

```python
def test_savings_report_ipmvp_compliant():
    """Generated savings report passes IPMVP Option C structural checks."""
    report = verify.generate_report("customer_x_building_a", period="2026-Q1")
    assert report.baseline_r_squared >= 0.75
    assert report.has_weather_normalization
    assert report.confidence_interval_method == "ASHRAE_14"
    assert report.savings_pct > 0
    assert report.audit_trail_complete
```

### Falsifiability gate
- Reports generate without manual intervention for any building with ≥3 months baseline.
- Third-party energy auditor (hire one for $5K spot review) signs off on the methodology before first customer-paid report.
- Reports survive customer's energy consultant review (the test that matters).

---

## Subsystem 5 — DASHBOARD

### What it does
The customer-facing UI. The thing investors see in the demo. The thing operators interact with daily.

### Pages

1. **Overview** — single-glance: today's energy vs baseline, savings $ YTD, comfort violations count, pending operator approvals.
2. **Twin state** — live readout of the twin's belief about the building. Per-zone temp, predicted next-hour energy, equipment status.
3. **Optimize** — the recommendation queue. Each pending change shows: what's being changed, predicted savings, predicted comfort impact, confidence. Operator approve / reject / modify.
4. **Verify** — savings reports, M&V audit, compliance reports.
5. **Compliance** — jurisdiction-aware: NYC LL97 emissions trajectory, BERDO letter grade, EPBD energy class. Forecast through deadline with current trajectory vs required.
6. **Settings** — point mappings, schedules, comfort bounds, integration health.

### Stack
- Frontend: Next.js + React + Recharts. Hosted on Vercel.
- Backend: FastAPI (existing in the REASONER-JEPA-NEXT codebase — reuse the patterns).
- Auth: Clerk or Auth0 (skip building auth from scratch).
- DB: Postgres + TimescaleDB.
- Hosting: Fly.io or Railway for backend; Vercel for frontend; Modal for ML inference.

### Acceptance test

- 5-minute live demo: ingest a building → fit twin → show recommendations → approve → see savings projection. End-to-end, no manual steps. (Modulo the 24h fit time, which is shown as an in-progress bar.)

### Falsifiability gate
- One end-to-end demo recording uploaded to landing page by week 2.
- First customer log-in and full operator workflow by week 7 (pilot #1 onboarding).

---

## Cross-cutting concerns

### Substrate versioning

REASONER-JEPA-NEXT is a separate repo and separate model artifact. Versions are tagged and reproducible:
- `reasoner_jepa_next/v0.2.0/s100m_stage1.ckpt`
- `reasoner_jepa_next/v0.2.0/s100m_stage2.ckpt`
- `reasoner_jepa_next/v0.2.0/s100m_stage3.ckpt`

TwinForge pins a specific version. Substrate upgrades are explicit, reviewed, A/B tested on customer data before rollout.

### Per-customer data isolation

Every customer's BMS data is stored in a separate logical schema. No cross-customer data leakage. Substrate fine-tuning produces a per-building adapter; the substrate weights themselves are never updated by customer data without explicit consent.

This matters for:
- Customer trust (their building's data isn't training a competitor's model).
- Liability (clear data-use boundaries).
- Federal contract eligibility (FedRAMP-adjacent customers require this).

### Safety / fallback hierarchy

1. **First line:** twin recommendations require operator approval (90 days minimum).
2. **Second line:** operator can globally pause TwinForge. Setpoints revert to BMS defaults instantly.
3. **Third line:** continuous comfort-violation monitoring. If violations exceed threshold, twin auto-pauses and pages support.
4. **Fourth line:** classical MPC fallback if the substrate's confidence drops (energy-head uncertainty above threshold).

This is non-negotiable. One bad week of comfort complaints kills a pilot and the reference call that depended on it.

### Telemetry & observability

- Datadog or similar for infrastructure monitoring.
- Per-building dashboards for the team: ingest rate, fit success, recommendation acceptance rate, savings trajectory.
- Alert on: ingest gap >2h, fit failure, comfort violation, substrate uncertainty spike, customer dashboard error rate >1%.

---

## Build sequence — 90-day breakdown

### Weeks 1–2: INGEST + DASHBOARD shell + demo TWIN (Mode A)

- INGEST: CSV upload only.
- TWIN: 50-state RC network in JAX.
- OPTIMIZE: classical MPC via CasADi.
- VERIFY: skip for demo.
- DASHBOARD: Overview + Twin-state + Optimize page (read-only).

**Demo on LBNL Building 59 by end of week 2.**

### Weeks 3–4: substrate integration + closed-loop demo

- TWIN Mode B: REASONER-JEPA-NEXT-S100M wired in (after the data plan's S100M ablation lands).
- OPTIMIZE: substrate-guided proposal + Langevin refinement.
- DASHBOARD: Optimize page becomes interactive (approve/reject).

**Demo upgraded by end of week 4. This is the demo investors see.**

### Weeks 5–7: BACnet integration + first pilot prep

- INGEST: BACnet/IP read-only.
- VERIFY: skeleton report generation.
- DASHBOARD: Verify page + Compliance page (NYC LL97 first).
- Per-customer schema isolation.

**First pilot deployment-ready by end of week 7.**

### Weeks 8–10: pilot #1 deployment & shadow mode

- Real customer data flowing.
- 30 days of shadow mode = first real trust check.
- Operator-approval workflow live.

### Weeks 11–12: closed-loop + verified savings

- First closed-loop setpoint changes (with operator approval).
- First IPMVP-compliant savings report.

---

## What gets built post-MVP (deliberately deferred)

These are explicitly NOT in the 90-day MVP:

- Modbus / proprietary BMS adapters (post-week 12).
- Multi-tenancy admin tools / agency view (when customer #5+ lands).
- Mobile app.
- Carbon accounting beyond LL97/BERDO/EPBD.
- Automated demand-response / utility-program integration.
- District-heating, data-center cooling, industrial-process variants.
- Cross-customer benchmarking (privacy-careful, post-revenue).
- The full S1B / S7B substrate scale-up (per data plan, that's months 3–12).

The MVP wins by being **narrow, deep, and verifiable.** Every feature defers that doesn't directly contribute to "this twin saves measurably more energy than the baseline, and we can prove it."

---

## Engineering hires (per the deck's hire plan)

The MVP is doable solo with reach. Day-90 → Day-180 hires:

| Hire | Role | Owns |
|---|---|---|
| #1 (Day 60–90) | ML engineer | TWIN substrate fine-tune; per-building adapter pipeline |
| #2 (Day 75–105) | BMS / controls engineer | INGEST BACnet adapter; on-site customer success |
| #3 (Day 90–120) | Founding GTM | Pilot pipeline; deals; customer success |
| #4 (Day 120–150) | Full-stack engineer | DASHBOARD; VERIFY reports |
| #5 (Day 150–180) | Senior systems engineer | Reliability; observability; deployment |

Total burn for 5 hires + founder + tooling + cloud: ~$200K/mo at full ramp; ~$2.4M/yr.

---

## Falsifiability gates — when to stop and rethink

Three gates that, if not cleared, mean the MVP plan needs revision before more spending.

### Gate 1 (Week 4): Substrate earns its keep

Can REASONER-JEPA-NEXT-S100M, fine-tuned for a building, beat a randomly-initialized identical-architecture model on held-out energy prediction? **If yes:** substrate is the moat, proceed. **If no:** the substrate isn't doing what we claim. Either fix the substrate (see data plan ablation gates) or rewrite the pitch around classical MPC.

### Gate 2 (Week 8): First real customer accepts the demo

The first pilot prospect has seen the demo, agreed to a paid POC, and BACnet integration succeeds. **If yes:** the wedge is real, scale. **If no:** the messaging or the buyer profile is wrong. Diagnose before week 10 fundraising.

### Gate 3 (Week 12): Verified savings on real building

Pilot #1's first month of shadow-mode data shows ≥5% energy reduction relative to IPMVP-baseline. **If yes:** the product works. The Series A narrative writes itself. **If no:** investigate. Most likely cause: building is genuinely already well-tuned (some are; ~10–15% of the population). Pivot to portfolios where average building is less optimized; or refine the optimizer.

---

*v1.0 — TwinForge MVP product specification. This is the engineering bible for days 1–90. Update when reality diverges.*
