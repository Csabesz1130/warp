import { Card, KPI } from "@/components/Card";
import { ComplianceChart } from "@/components/EnergyChart";
import { compliance } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export default function CompliancePage() {
  const c = compliance();
  const totalBaselineFine = c.fineForecastUsd.reduce((a, x) => a + x.baselineFineUsd, 0);
  const totalOptimizedFine = c.fineForecastUsd.reduce((a, x) => a + x.optimizedFineUsd, 0);
  const avoided = totalBaselineFine - totalOptimizedFine;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Compliance</h1>
        <p className="text-forge-muted text-sm mt-1">
          {c.jurisdiction.replace("_", " ")} · current grade <span className="text-forge-text">{c.letterGradeOrClass}</span> · trajectory through 2030
        </p>
      </div>

      <div className="kpi-grid">
        <KPI
          label="Cumulative fines (no twin)"
          value={`$${(totalBaselineFine / 1e6).toFixed(2)}M`}
          delta="2024–2030, baseline trajectory"
          tone="bad"
        />
        <KPI
          label="Cumulative fines (with twin)"
          value={`$${(totalOptimizedFine / 1e6).toFixed(2)}M`}
          delta="2024–2030, optimized trajectory"
          tone="warn"
        />
        <KPI
          label="Fines avoided"
          value={`$${(avoided / 1e6).toFixed(2)}M`}
          delta="vs baseline"
          tone="good"
        />
      </div>

      <Card title="Emissions vs LL97 budget">
        <ComplianceChart data={c.yearlyEmissionsTonnes} />
      </Card>

      <Card title="Yearly fine forecast (USD)">
        <table className="w-full text-sm">
          <thead className="text-forge-muted text-xs uppercase tracking-wide">
            <tr className="border-b border-forge-border">
              <th className="text-left py-2 font-normal">Year</th>
              <th className="text-right py-2 font-normal">Budget (t CO₂)</th>
              <th className="text-right py-2 font-normal">Projected (t CO₂)</th>
              <th className="text-right py-2 font-normal">Baseline fine</th>
              <th className="text-right py-2 font-normal">Optimized fine</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forge-border">
            {c.yearlyEmissionsTonnes.map((row, i) => {
              const fine = c.fineForecastUsd[i];
              return (
                <tr key={row.year}>
                  <td className="py-2 font-mono text-xs">{row.year}</td>
                  <td className="py-2 text-right tabular-nums">{row.budgetTonnes}</td>
                  <td className="py-2 text-right tabular-nums">{row.projectedTonnes}</td>
                  <td className="py-2 text-right tabular-nums text-forge-danger/80">
                    {fine.baselineFineUsd > 0 ? `$${fine.baselineFineUsd.toLocaleString()}` : "—"}
                  </td>
                  <td className="py-2 text-right tabular-nums text-forge-ok">
                    {fine.optimizedFineUsd > 0 ? `$${fine.optimizedFineUsd.toLocaleString()}` : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
