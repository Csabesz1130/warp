export type Building = {
  id: string;
  name: string;
  city: string;
  sqft: number;
  jurisdiction: "NYC_LL97" | "BERDO" | "EPBD" | "NONE";
  baselineKwhPerSqftYr: number;
};

export type EnergySample = {
  ts: string;
  baselineKw: number;
  actualKw: number;
  forecastKw: number;
};

export type ZoneState = {
  id: string;
  name: string;
  floor: number;
  tempC: number;
  setpointC: number;
  occupancy: number;
  comfortStatus: "ok" | "warn" | "violation";
};

export type EquipmentState = {
  id: string;
  name: string;
  kind: "AHU" | "CHILLER" | "BOILER" | "PUMP" | "VAV";
  status: "running" | "idle" | "fault";
  loadPct: number;
  driftDays: number | null;
};

export type Recommendation = {
  id: string;
  zone: string;
  changeSummary: string;
  predictedSavingsKwhDay: number;
  predictedComfortDeltaC: number;
  confidence: number;
  rationale: string;
  status: "pending" | "approved" | "rejected" | "applied";
  createdAt: string;
};

export type SavingsReport = {
  period: string;
  baselineKwh: number;
  measuredKwh: number;
  avoidedKwh: number;
  savingsPct: number;
  ciLowPct: number;
  ciHighPct: number;
  baselineRSquared: number;
  ipmvpOption: "C";
  generatedAt: string;
};

export type ComplianceTrajectory = {
  jurisdiction: "NYC_LL97" | "BERDO" | "EPBD";
  letterGradeOrClass: string;
  yearlyEmissionsTonnes: { year: number; budgetTonnes: number; projectedTonnes: number }[];
  fineForecastUsd: { year: number; baselineFineUsd: number; optimizedFineUsd: number }[];
};

export type Overview = {
  building: Building;
  todayKwhBaseline: number;
  todayKwhMeasured: number;
  ytdSavingsUsd: number;
  ytdSavingsPct: number;
  comfortViolations24h: number;
  pendingApprovals: number;
  twinFitAgeHours: number;
  energy24h: EnergySample[];
};
