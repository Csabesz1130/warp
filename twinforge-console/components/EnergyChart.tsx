"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { EnergySample } from "@/lib/types";

function fmtTime(ts: string) {
  const d = new Date(ts);
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function EnergyChart({ samples }: { samples: EnergySample[] }) {
  const data = samples.map((s) => ({
    t: fmtTime(s.ts),
    baseline: s.baselineKw,
    actual: s.actualKw,
    forecast: s.forecastKw,
  }));
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="gActual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22d3a8" stopOpacity={0.45} />
              <stop offset="100%" stopColor="#22d3a8" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="gBaseline" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#7c8cf8" stopOpacity={0.25} />
              <stop offset="100%" stopColor="#7c8cf8" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1f2a37" vertical={false} />
          <XAxis dataKey="t" stroke="#7d8898" fontSize={11} tickLine={false} axisLine={false} interval={11} />
          <YAxis stroke="#7d8898" fontSize={11} tickLine={false} axisLine={false} unit=" kW" width={60} />
          <Tooltip
            contentStyle={{
              background: "#11171f",
              border: "1px solid #1f2a37",
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: "#7d8898" }}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "#7d8898" }} />
          <Area
            type="monotone"
            dataKey="baseline"
            stroke="#7c8cf8"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            fill="url(#gBaseline)"
            name="Baseline (no twin)"
          />
          <Area
            type="monotone"
            dataKey="actual"
            stroke="#22d3a8"
            strokeWidth={2}
            fill="url(#gActual)"
            name="Optimized (twin)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ComplianceChart({
  data,
}: {
  data: { year: number; budgetTonnes: number; projectedTonnes: number }[];
}) {
  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="#1f2a37" vertical={false} />
          <XAxis dataKey="year" stroke="#7d8898" fontSize={11} tickLine={false} axisLine={false} />
          <YAxis stroke="#7d8898" fontSize={11} tickLine={false} axisLine={false} unit=" t" width={60} />
          <Tooltip
            contentStyle={{
              background: "#11171f",
              border: "1px solid #1f2a37",
              borderRadius: 8,
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "#7d8898" }} />
          <Line
            type="monotone"
            dataKey="budgetTonnes"
            stroke="#f5a524"
            strokeWidth={2}
            dot={false}
            name="LL97 budget"
          />
          <Line
            type="monotone"
            dataKey="projectedTonnes"
            stroke="#22d3a8"
            strokeWidth={2}
            dot={{ r: 3, fill: "#22d3a8" }}
            name="Projected (with twin)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
