import type {
  Building,
  ComplianceTrajectory,
  EnergySample,
  EquipmentState,
  Overview,
  Recommendation,
  SavingsReport,
  ZoneState,
} from "./types";

export const BUILDING: Building = {
  id: "lbnl_b59",
  name: "LBNL Building 59",
  city: "Berkeley, CA",
  sqft: 124_000,
  jurisdiction: "NYC_LL97",
  baselineKwhPerSqftYr: 18.4,
};

function seedRand(seed: number) {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 0xffffffff;
  };
}

export function energy24h(): EnergySample[] {
  const rand = seedRand(42);
  const out: EnergySample[] = [];
  const now = new Date();
  for (let i = 95; i >= 0; i--) {
    const ts = new Date(now.getTime() - i * 15 * 60_000);
    const hour = ts.getHours() + ts.getMinutes() / 60;
    const occ = Math.max(0, Math.sin(((hour - 6) / 14) * Math.PI));
    const baseline = 240 + 180 * occ + (rand() - 0.5) * 22;
    const actual = baseline * (0.78 + (rand() - 0.5) * 0.04);
    const forecast = actual * (0.99 + (rand() - 0.5) * 0.01);
    out.push({
      ts: ts.toISOString(),
      baselineKw: round(baseline, 1),
      actualKw: round(actual, 1),
      forecastKw: round(forecast, 1),
    });
  }
  return out;
}

export function overview(): Overview {
  const samples = energy24h();
  const sumK = (k: keyof EnergySample) =>
    samples.reduce((a, s) => a + Number(s[k] ?? 0), 0) * 0.25;
  const todayKwhBaseline = round(sumK("baselineKw"), 0);
  const todayKwhMeasured = round(sumK("actualKw"), 0);
  return {
    building: BUILDING,
    todayKwhBaseline,
    todayKwhMeasured,
    ytdSavingsUsd: 184_220,
    ytdSavingsPct: 17.4,
    comfortViolations24h: 1,
    pendingApprovals: 3,
    twinFitAgeHours: 6.2,
    energy24h: samples,
  };
}

export function zones(): ZoneState[] {
  const rand = seedRand(7);
  const names = [
    "Lobby",
    "Open office N",
    "Open office S",
    "Conf 201",
    "Conf 202",
    "Lab 301",
    "Lab 302",
    "Lab 303",
    "Server room",
    "Kitchen",
    "Atrium",
    "Mech room",
  ];
  return names.map((name, i) => {
    const setpoint = 22 + (i % 3) * 0.5;
    const drift = (rand() - 0.5) * 1.6;
    const temp = round(setpoint + drift, 2);
    const violation = Math.abs(drift) > 1.0;
    const warn = Math.abs(drift) > 0.6 && !violation;
    return {
      id: `zone_${i + 1}`,
      name,
      floor: Math.floor(i / 4) + 1,
      tempC: temp,
      setpointC: setpoint,
      occupancy: round(Math.max(0, rand()), 2),
      comfortStatus: violation ? "violation" : warn ? "warn" : "ok",
    };
  });
}

export function equipment(): EquipmentState[] {
  return [
    { id: "AHU-1", name: "AHU-1 East", kind: "AHU", status: "running", loadPct: 62, driftDays: 14 },
    { id: "AHU-2", name: "AHU-2 West", kind: "AHU", status: "running", loadPct: 71, driftDays: 4 },
    { id: "CH-1", name: "Chiller 1", kind: "CHILLER", status: "running", loadPct: 48, driftDays: 22 },
    { id: "CH-2", name: "Chiller 2", kind: "CHILLER", status: "idle", loadPct: 0, driftDays: 22 },
    { id: "B-1", name: "Boiler 1", kind: "BOILER", status: "idle", loadPct: 0, driftDays: 60 },
    { id: "P-CHW", name: "CHW pump", kind: "PUMP", status: "running", loadPct: 55, driftDays: null },
    { id: "P-HHW", name: "HHW pump", kind: "PUMP", status: "fault", loadPct: 0, driftDays: null },
  ];
}

export function recommendations(): Recommendation[] {
  return [
    {
      id: "rec_001",
      zone: "Open office N",
      changeSummary: "Pre-cool to 21.5°C 06:00–07:30, then 22.5°C until 17:00",
      predictedSavingsKwhDay: 142,
      predictedComfortDeltaC: 0.2,
      confidence: 0.91,
      rationale:
        "Pre-cool exploits 5–7 AM low-grid period; setpoint band stays within ±1°C; load shift cuts peak demand charge.",
      status: "pending",
      createdAt: new Date(Date.now() - 18 * 60_000).toISOString(),
    },
    {
      id: "rec_002",
      zone: "Conf 201",
      changeSummary: "Reduce ventilation 30% during unoccupied hours 19:00–06:00",
      predictedSavingsKwhDay: 38,
      predictedComfortDeltaC: 0.0,
      confidence: 0.97,
      rationale: "Occupancy sensor confirms <2% utilization in this band; ASHRAE 62.1 minimum still met.",
      status: "pending",
      createdAt: new Date(Date.now() - 41 * 60_000).toISOString(),
    },
    {
      id: "rec_003",
      zone: "Chiller plant",
      changeSummary: "Raise CHW supply temp from 6.5°C to 7.5°C during partial-load hours",
      predictedSavingsKwhDay: 96,
      predictedComfortDeltaC: 0.1,
      confidence: 0.83,
      rationale: "Partial load < 60% across forecast horizon; lift reduction improves COP without hitting reset limits.",
      status: "pending",
      createdAt: new Date(Date.now() - 95 * 60_000).toISOString(),
    },
    {
      id: "rec_004",
      zone: "AHU-2 West",
      changeSummary: "Enable economizer when OAT < 16°C and ΔH > 4 kJ/kg",
      predictedSavingsKwhDay: 73,
      predictedComfortDeltaC: 0.0,
      confidence: 0.94,
      rationale: "Forecast shows 11h of free-cooling-eligible weather over next 48h.",
      status: "applied",
      createdAt: new Date(Date.now() - 6 * 3600_000).toISOString(),
    },
  ];
}

export function savingsReport(): SavingsReport {
  return {
    period: "2026-Q1",
    baselineKwh: 1_864_500,
    measuredKwh: 1_543_120,
    avoidedKwh: 321_380,
    savingsPct: 17.2,
    ciLowPct: 14.1,
    ciHighPct: 20.4,
    baselineRSquared: 0.83,
    ipmvpOption: "C",
    generatedAt: new Date().toISOString(),
  };
}

export function compliance(): ComplianceTrajectory {
  const startBudget = 410;
  const ramp = (year: number) => Math.max(180, startBudget - (year - 2024) * 28);
  const yearlyEmissionsTonnes = [];
  const fineForecastUsd = [];
  for (let y = 2024; y <= 2030; y++) {
    const budget = ramp(y);
    const projected = Math.max(170, 470 - (y - 2024) * 22);
    yearlyEmissionsTonnes.push({
      year: y,
      budgetTonnes: budget,
      projectedTonnes: projected,
    });
    const overBaseline = Math.max(0, projected + 80 - budget);
    const overOptimized = Math.max(0, projected - budget);
    fineForecastUsd.push({
      year: y,
      baselineFineUsd: round(overBaseline * 268, 0),
      optimizedFineUsd: round(overOptimized * 268, 0),
    });
  }
  return {
    jurisdiction: "NYC_LL97",
    letterGradeOrClass: "B",
    yearlyEmissionsTonnes,
    fineForecastUsd,
  };
}

function round(x: number, p: number) {
  const f = Math.pow(10, p);
  return Math.round(x * f) / f;
}
