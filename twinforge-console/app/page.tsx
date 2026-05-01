import { Card, KPI } from "@/components/Card";
import { EnergyChart } from "@/components/EnergyChart";
import { overview } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export default function OverviewPage() {
  const o = overview();
  const savedKwh = Math.max(0, o.todayKwhBaseline - o.todayKwhMeasured);
  const pctToday = ((savedKwh / o.todayKwhBaseline) * 100).toFixed(1);

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-xl font-semibold">Overview</h1>
          <p className="text-forge-muted text-sm mt-1">
            Twin running in approval mode · operator approves each setpoint change
          </p>
        </div>
        <div className="text-xs text-forge-muted font-mono">
          {new Date().toLocaleString()}
        </div>
      </div>

      <div className="kpi-grid">
        <KPI
          label="Today vs baseline"
          value={`${pctToday}%`}
          delta={`${savedKwh.toLocaleString()} kWh avoided`}
          tone="good"
        />
        <KPI
          label="YTD savings"
          value={`$${o.ytdSavingsUsd.toLocaleString()}`}
          delta={`${o.ytdSavingsPct}% reduction`}
          tone="good"
        />
        <KPI
          label="Comfort violations (24h)"
          value={String(o.comfortViolations24h)}
          delta={o.comfortViolations24h === 0 ? "all zones in band" : "1 zone, 14 min"}
          tone={o.comfortViolations24h === 0 ? "good" : "warn"}
        />
        <KPI
          label="Pending approvals"
          value={String(o.pendingApprovals)}
          delta="awaiting operator review"
          tone={o.pendingApprovals > 0 ? "warn" : "neutral"}
        />
        <KPI
          label="Twin fit age"
          value={`${o.twinFitAgeHours.toFixed(1)} h`}
          delta="next refit in 17.8 h"
          tone="neutral"
        />
      </div>

      <Card
        title="Energy — last 24 h"
        right={
          <div className="flex items-center gap-3 text-xs text-forge-muted">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-3 bg-forge-accent rounded-sm" /> Optimized
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-3 bg-forge-accent2/60 rounded-sm" /> Baseline
            </span>
          </div>
        }
      >
        <EnergyChart samples={o.energy24h} />
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Twin status">
          <ul className="text-sm space-y-2">
            <Row label="Substrate version" value="reasoner-jepa-next v0.2.0 / s100m-stage3" mono />
            <Row label="Adapter parameters" value="2.4M trainable" mono />
            <Row label="Last refit" value="6.2 h ago · 23 min" />
            <Row label="Held-out 7d energy MAPE" value="6.8%" tone="good" />
            <Row label="Zone temp RMSE (24h)" value="0.42 °C" tone="good" />
            <Row label="Substrate confidence" value="0.91 (calibrated)" tone="good" />
          </ul>
        </Card>
        <Card title="Recent activity">
          <ul className="text-sm divide-y divide-forge-border">
            <Activity ts="08:14" text="Recommendation rec_001 created (Open office N pre-cool)" />
            <Activity ts="07:30" text="Operator approved rec_004 (AHU-2 economizer)" tone="good" />
            <Activity ts="06:02" text="Twin refit complete — MAPE 6.8% on held-out week" tone="good" />
            <Activity ts="03:11" text="Substrate uncertainty spike on Lab 302 — fallback engaged" tone="warn" />
            <Activity ts="00:44" text="BMS ingest gap recovered after 4 min" />
          </ul>
        </Card>
      </div>
    </div>
  );
}

function Row({
  label,
  value,
  mono,
  tone,
}: {
  label: string;
  value: string;
  mono?: boolean;
  tone?: "good" | "warn" | "bad";
}) {
  const toneClass =
    tone === "good"
      ? "text-forge-ok"
      : tone === "warn"
        ? "text-forge-warn"
        : tone === "bad"
          ? "text-forge-danger"
          : "text-forge-text";
  return (
    <li className="flex justify-between gap-4">
      <span className="text-forge-muted">{label}</span>
      <span className={`${mono ? "font-mono text-xs" : ""} ${toneClass}`}>{value}</span>
    </li>
  );
}

function Activity({
  ts,
  text,
  tone,
}: {
  ts: string;
  text: string;
  tone?: "good" | "warn";
}) {
  const dotColor =
    tone === "good"
      ? "bg-forge-ok"
      : tone === "warn"
        ? "bg-forge-warn"
        : "bg-forge-muted";
  return (
    <li className="py-2 flex items-center gap-3">
      <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`} />
      <span className="font-mono text-xs text-forge-muted w-12">{ts}</span>
      <span className="flex-1">{text}</span>
    </li>
  );
}
