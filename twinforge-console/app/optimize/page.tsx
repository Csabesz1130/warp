"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/Card";
import type { Recommendation } from "@/lib/types";

export default function OptimizePage() {
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/recommendations")
      .then((r) => r.json())
      .then((j) => setRecs(j.recommendations))
      .finally(() => setLoading(false));
  }, []);

  async function decide(id: string, action: "approve" | "reject") {
    const optimistic = recs.map((r) =>
      r.id === id ? { ...r, status: action === "approve" ? "approved" : "rejected" } : r
    ) as Recommendation[];
    setRecs(optimistic);
    await fetch("/api/recommendations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, action }),
    });
  }

  const pending = recs.filter((r) => r.status === "pending");
  const decided = recs.filter((r) => r.status !== "pending");
  const totalSavings = pending.reduce((a, r) => a + r.predictedSavingsKwhDay, 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Optimize</h1>
        <p className="text-forge-muted text-sm mt-1">
          {pending.length} pending changes — {Math.round(totalSavings)} kWh/day if all approved
        </p>
      </div>

      <Card title={`Pending recommendations (${pending.length})`}>
        {loading ? (
          <div className="text-forge-muted text-sm">Loading…</div>
        ) : pending.length === 0 ? (
          <div className="text-forge-muted text-sm">Nothing pending. Twin is keeping up with the building.</div>
        ) : (
          <ul className="space-y-3">
            {pending.map((r) => (
              <RecCard key={r.id} rec={r} onDecide={decide} />
            ))}
          </ul>
        )}
      </Card>

      {decided.length > 0 && (
        <Card title={`Recent decisions (${decided.length})`}>
          <ul className="text-sm divide-y divide-forge-border">
            {decided.map((r) => (
              <li key={r.id} className="py-2 flex items-center gap-3">
                <StatusBadge status={r.status} />
                <span className="text-forge-muted text-xs font-mono">{r.id}</span>
                <span className="flex-1 truncate">
                  {r.zone} — {r.changeSummary}
                </span>
                <span className="text-xs text-forge-muted">
                  {r.predictedSavingsKwhDay} kWh/day
                </span>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}

function RecCard({
  rec,
  onDecide,
}: {
  rec: Recommendation;
  onDecide: (id: string, action: "approve" | "reject") => void;
}) {
  return (
    <li className="border border-forge-border rounded-md p-4 bg-forge-panel2/40">
      <div className="flex justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-mono text-xs text-forge-muted">{rec.id}</span>
            <span className="text-xs text-forge-muted">·</span>
            <span className="text-sm font-medium">{rec.zone}</span>
          </div>
          <div className="mt-1 text-sm">{rec.changeSummary}</div>
          <p className="mt-2 text-xs text-forge-muted leading-relaxed">{rec.rationale}</p>
        </div>
        <div className="text-right text-xs space-y-1 min-w-[160px]">
          <div>
            <div className="text-forge-muted">Savings</div>
            <div className="text-forge-ok font-semibold tabular-nums">
              {rec.predictedSavingsKwhDay} kWh/day
            </div>
          </div>
          <div>
            <div className="text-forge-muted">Comfort Δ</div>
            <div className="tabular-nums">
              {rec.predictedComfortDeltaC === 0
                ? "no change"
                : `${rec.predictedComfortDeltaC > 0 ? "+" : ""}${rec.predictedComfortDeltaC}°C`}
            </div>
          </div>
          <div>
            <div className="text-forge-muted">Confidence</div>
            <ConfidenceBar value={rec.confidence} />
          </div>
        </div>
      </div>
      <div className="mt-3 flex gap-2 justify-end">
        <button
          onClick={() => onDecide(rec.id, "reject")}
          className="px-3 py-1.5 text-xs rounded-md border border-forge-border text-forge-muted hover:text-forge-text hover:border-forge-danger/50"
        >
          Reject
        </button>
        <button
          onClick={() => onDecide(rec.id, "approve")}
          className="px-3 py-1.5 text-xs rounded-md bg-forge-accent/15 text-forge-accent border border-forge-accent/40 hover:bg-forge-accent/25"
        >
          Approve & apply
        </button>
      </div>
    </li>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = value > 0.9 ? "bg-forge-ok" : value > 0.75 ? "bg-forge-accent2" : "bg-forge-warn";
  return (
    <div className="w-full mt-1">
      <div className="h-1.5 bg-forge-border rounded">
        <div className={`h-1.5 rounded ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="text-right tabular-nums mt-0.5">{pct}%</div>
    </div>
  );
}

function StatusBadge({ status }: { status: Recommendation["status"] }) {
  const map: Record<Recommendation["status"], string> = {
    pending: "bg-forge-warn/15 text-forge-warn",
    approved: "bg-forge-ok/15 text-forge-ok",
    applied: "bg-forge-ok/15 text-forge-ok",
    rejected: "bg-forge-danger/15 text-forge-danger",
  };
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs ${map[status]}`}>{status}</span>
  );
}
