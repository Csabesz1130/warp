"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Overview", glyph: "◐" },
  { href: "/twin", label: "Twin state", glyph: "◇" },
  { href: "/optimize", label: "Optimize", glyph: "↯" },
  { href: "/verify", label: "Verify", glyph: "✓" },
  { href: "/compliance", label: "Compliance", glyph: "§" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-56 shrink-0 bg-forge-panel border-r border-forge-border flex flex-col">
      <div className="px-5 py-5 border-b border-forge-border">
        <div className="text-forge-accent font-semibold tracking-wide text-lg">TwinForge</div>
        <div className="text-forge-muted text-xs mt-1">Operator Console · v0.1</div>
      </div>
      <nav className="flex-1 p-2">
        {NAV.map((n) => {
          const active = pathname === n.href;
          return (
            <Link
              key={n.href}
              href={n.href as any}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-forge-panel2 text-forge-text"
                  : "text-forge-muted hover:bg-forge-panel2 hover:text-forge-text"
              }`}
            >
              <span className={active ? "text-forge-accent" : ""}>{n.glyph}</span>
              <span>{n.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-forge-border text-xs text-forge-muted">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-forge-accent animate-pulse" />
          Substrate: REASONER-JEPA-NEXT S100M
        </div>
        <div className="mt-1 opacity-70">v0.2.0 · stage 3</div>
      </div>
    </aside>
  );
}
