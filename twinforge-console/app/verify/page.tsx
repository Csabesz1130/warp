import { Card, KPI } from "@/components/Card";
import { savingsReport } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export default function VerifyPage() {
  const r = savingsReport();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Verify</h1>
        <p className="text-forge-muted text-sm mt-1">
          IPMVP Option C · ASHRAE Guideline 14 confidence intervals · auditable savings.
        </p>
      </div>

      <div className="kpi-grid">
        <KPI
          label={`Avoided energy · ${r.period}`}
          value={`${r.avoidedKwh.toLocaleString()} kWh`}
          delta={`${r.savingsPct.toFixed(1)}% (${r.ciLowPct.toFixed(1)}–${r.ciHighPct.toFixed(1)}% @ 90% CI)`}
          tone="good"
        />
        <KPI
          label="Baseline regression R²"
          value={r.baselineRSquared.toFixed(2)}
          delta={r.baselineRSquared >= 0.75 ? "exceeds IPMVP minimum" : "below IPMVP minimum"}
          tone={r.baselineRSquared >= 0.75 ? "good" : "warn"}
        />
        <KPI
          label="Method"
          value={`IPMVP Option ${r.ipmvpOption}`}
          delta="weather + occupancy normalized"
        />
        <KPI
          label="Avoided $"
          value={`$${Math.round(r.avoidedKwh * 0.18).toLocaleString()}`}
          delta="@ $0.18/kWh blended rate"
          tone="good"
        />
      </div>

      <Card title="Methodology">
        <ol className="text-sm space-y-2 list-decimal list-inside text-forge-muted">
          <li>Baseline: 12 months pre-deployment energy regressed against weather, occupancy, time-of-day, day-of-week.</li>
          <li>Adjusted baseline: regression applied to post-deployment weather + occupancy.</li>
          <li>Avoided energy = adjusted baseline − measured (whole-facility metering).</li>
          <li>Confidence interval per ASHRAE Guideline 14, reported at 90%.</li>
          <li>Audit trail of every setpoint change, operator approval, and predicted-vs-actual delta.</li>
        </ol>
      </Card>

      <Card
        title="Reports"
        right={
          <button className="text-xs px-3 py-1.5 rounded border border-forge-border hover:border-forge-accent/60">
            Generate PDF
          </button>
        }
      >
        <ul className="text-sm divide-y divide-forge-border">
          <li className="py-2 flex justify-between">
            <span>2026-Q1 Verified Savings Report</span>
            <span className="text-forge-muted text-xs">Generated {new Date(r.generatedAt).toLocaleDateString()}</span>
          </li>
          <li className="py-2 flex justify-between">
            <span>2025-Q4 Verified Savings Report</span>
            <span className="text-forge-muted text-xs">Audited · third-party</span>
          </li>
          <li className="py-2 flex justify-between">
            <span>Annual M&V Audit Package · 2025</span>
            <span className="text-forge-muted text-xs">IPMVP-compliant</span>
          </li>
        </ul>
      </Card>
    </div>
  );
}
