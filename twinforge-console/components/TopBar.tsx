import type { Building } from "@/lib/types";

export function TopBar({ building }: { building: Building }) {
  return (
    <header className="h-14 border-b border-forge-border bg-forge-panel flex items-center px-6 justify-between">
      <div className="flex items-center gap-3">
        <div className="text-sm font-medium">{building.name}</div>
        <div className="text-xs text-forge-muted">
          {building.city} · {building.sqft.toLocaleString()} sq ft · {building.jurisdiction.replace("_", " ")}
        </div>
      </div>
      <div className="flex items-center gap-4 text-xs text-forge-muted">
        <span className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-forge-ok" />
          BMS connected · 412 points
        </span>
        <span>Twin fit · 6.2h ago</span>
      </div>
    </header>
  );
}
