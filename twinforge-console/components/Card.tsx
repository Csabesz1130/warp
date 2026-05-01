import { ReactNode } from "react";

export function Card({
  title,
  children,
  right,
  className = "",
}: {
  title?: string;
  children: ReactNode;
  right?: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`bg-forge-panel border border-forge-border rounded-lg p-4 ${className}`}
    >
      {(title || right) && (
        <header className="flex items-center justify-between mb-3">
          {title && <h2 className="text-sm font-medium text-forge-text">{title}</h2>}
          {right}
        </header>
      )}
      {children}
    </section>
  );
}

export function KPI({
  label,
  value,
  delta,
  tone = "neutral",
}: {
  label: string;
  value: string;
  delta?: string;
  tone?: "good" | "warn" | "bad" | "neutral";
}) {
  const toneClass =
    tone === "good"
      ? "text-forge-ok"
      : tone === "warn"
        ? "text-forge-warn"
        : tone === "bad"
          ? "text-forge-danger"
          : "text-forge-muted";
  return (
    <div className="bg-forge-panel border border-forge-border rounded-lg p-4">
      <div className="text-xs text-forge-muted">{label}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
      {delta && <div className={`mt-1 text-xs ${toneClass}`}>{delta}</div>}
    </div>
  );
}
