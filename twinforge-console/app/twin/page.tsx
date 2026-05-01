import { Card } from "@/components/Card";
import { equipment, zones } from "@/lib/mockData";

export const dynamic = "force-dynamic";

export default function TwinPage() {
  const z = zones();
  const e = equipment();
  const violations = z.filter((zz) => zz.comfortStatus === "violation").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Twin state</h1>
        <p className="text-forge-muted text-sm mt-1">
          Live readout of the twin's belief about the building. Updated every 15 minutes.
        </p>
      </div>

      <Card
        title={`Zones (${z.length})`}
        right={
          <span className="text-xs text-forge-muted">
            {violations} violations · {z.filter((zz) => zz.comfortStatus === "warn").length} warnings
          </span>
        }
      >
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {z.map((zz) => (
            <ZoneTile key={zz.id} zone={zz} />
          ))}
        </div>
      </Card>

      <Card title="Equipment">
        <table className="w-full text-sm">
          <thead className="text-forge-muted text-xs uppercase tracking-wide">
            <tr className="border-b border-forge-border">
              <th className="text-left py-2 font-normal">ID</th>
              <th className="text-left py-2 font-normal">Name</th>
              <th className="text-left py-2 font-normal">Kind</th>
              <th className="text-left py-2 font-normal">Status</th>
              <th className="text-right py-2 font-normal">Load</th>
              <th className="text-right py-2 font-normal">Drift</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-forge-border">
            {e.map((eq) => (
              <tr key={eq.id} className="hover:bg-forge-panel2/40">
                <td className="py-2 font-mono text-xs">{eq.id}</td>
                <td className="py-2">{eq.name}</td>
                <td className="py-2 text-forge-muted text-xs">{eq.kind}</td>
                <td className="py-2">
                  <StatusPill status={eq.status} />
                </td>
                <td className="py-2 text-right font-mono text-xs">
                  {eq.status === "running" ? `${eq.loadPct}%` : "—"}
                </td>
                <td className="py-2 text-right text-xs text-forge-muted">
                  {eq.driftDays === null
                    ? "n/a"
                    : eq.driftDays > 30
                      ? `${eq.driftDays}d ⚠`
                      : `${eq.driftDays}d`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

function ZoneTile({ zone }: { zone: ReturnType<typeof zones>[number] }) {
  const tone =
    zone.comfortStatus === "violation"
      ? "border-forge-danger/60 bg-forge-danger/10"
      : zone.comfortStatus === "warn"
        ? "border-forge-warn/60 bg-forge-warn/10"
        : "border-forge-border bg-forge-panel2";
  const delta = zone.tempC - zone.setpointC;
  const deltaStr = `${delta >= 0 ? "+" : ""}${delta.toFixed(1)}°`;
  return (
    <div className={`border rounded-md p-3 ${tone}`}>
      <div className="flex justify-between items-baseline">
        <div className="text-sm font-medium">{zone.name}</div>
        <div className="text-xs text-forge-muted">F{zone.floor}</div>
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-semibold tabular-nums">{zone.tempC.toFixed(1)}°</span>
        <span className="text-xs text-forge-muted">/ {zone.setpointC.toFixed(1)}° sp</span>
      </div>
      <div className="mt-1 flex justify-between text-xs">
        <span
          className={
            zone.comfortStatus === "violation"
              ? "text-forge-danger"
              : zone.comfortStatus === "warn"
                ? "text-forge-warn"
                : "text-forge-muted"
          }
        >
          {deltaStr}
        </span>
        <span className="text-forge-muted">occ {Math.round(zone.occupancy * 100)}%</span>
      </div>
    </div>
  );
}

function StatusPill({ status }: { status: "running" | "idle" | "fault" }) {
  const map = {
    running: "bg-forge-ok/15 text-forge-ok",
    idle: "bg-forge-muted/15 text-forge-muted",
    fault: "bg-forge-danger/15 text-forge-danger",
  };
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs ${map[status]}`}>{status}</span>
  );
}
