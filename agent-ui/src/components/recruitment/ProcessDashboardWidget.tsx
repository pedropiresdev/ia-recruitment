"use client";

import { useRouter } from "next/navigation";
import type { RecruitmentProcess, SLAStatus } from "@/types/recruitment";
import { ProcessCard } from "./ProcessPanel/ProcessCard";

type KPIs = {
  total: number;
  em_atraso: number;
  em_risco: number;
  no_prazo: number;
};

type ProcessDashboardWidgetProps = {
  summary?: string;
  kpis: KPIs;
  items: RecruitmentProcess[];
};

const KPI_CONFIGS = [
  {
    key: "total" as const,
    label: "Total",
    colorClass: "text-primary",
    bgClass: "bg-background border-border",
    dot: null,
  },
  {
    key: "em_atraso" as const,
    label: "Com atraso",
    colorClass: "text-red-400",
    bgClass: "bg-red-500/5 border-red-500/20",
    dot: "bg-red-500",
  },
  {
    key: "em_risco" as const,
    label: "Em risco",
    colorClass: "text-yellow-400",
    bgClass: "bg-yellow-500/5 border-yellow-500/20",
    dot: "bg-yellow-500",
  },
  {
    key: "no_prazo" as const,
    label: "No prazo",
    colorClass: "text-green-400",
    bgClass: "bg-green-500/5 border-green-500/20",
    dot: "bg-green-500",
  },
];

const SLA_SECTIONS: {
  key: SLAStatus;
  label: string;
  labelClass: string;
}[] = [
  { key: "em_atraso", label: "SLA Vencido", labelClass: "text-red-400" },
  { key: "em_risco", label: "Em Risco", labelClass: "text-yellow-400" },
  { key: "no_prazo", label: "No Prazo", labelClass: "text-green-400" },
];

export function ProcessDashboardWidget({
  summary,
  kpis,
  items,
}: ProcessDashboardWidgetProps) {
  const router = useRouter();

  function handleAction(prompt: string) {
    router.push(`/?prompt=${encodeURIComponent(prompt)}`);
  }

  return (
    <div className="mt-2 rounded-xl border border-border bg-background-secondary overflow-hidden w-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-muted"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2"
            />
          </svg>
          <span className="text-sm font-semibold text-primary">
            Painel de Processos
          </span>
        </div>
        <a
          href="/processos"
          className="text-xs text-muted hover:text-primary transition-colors"
        >
          Ver painel completo →
        </a>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-px bg-border m-4 rounded-lg overflow-hidden">
        {KPI_CONFIGS.map((cfg) => (
          <div
            key={cfg.key}
            className={`flex flex-col items-center justify-center py-3 px-2 border ${cfg.bgClass} bg-background-secondary`}
          >
            <div className="flex items-center gap-1.5 mb-0.5">
              {cfg.dot && (
                <span
                  className={`inline-block w-2 h-2 rounded-full ${cfg.dot}`}
                />
              )}
              <span className={`text-xl font-bold ${cfg.colorClass}`}>
                {kpis[cfg.key]}
              </span>
            </div>
            <span className="text-[10px] text-muted text-center leading-tight">
              {cfg.label}
            </span>
          </div>
        ))}
      </div>

      {/* Summary line */}
      {summary && (
        <p className="px-4 pb-3 text-xs text-muted -mt-1">{summary}</p>
      )}

      {/* Process cards grouped by SLA */}
      <div className="px-4 pb-4 space-y-4">
        {SLA_SECTIONS.map((section) => {
          const sectionItems = items.filter(
            (p) => p.sla_status === section.key
          );
          if (sectionItems.length === 0) return null;
          return (
            <div key={section.key}>
              <p
                className={`text-[10px] font-semibold uppercase tracking-widest mb-2 ${section.labelClass}`}
              >
                {section.label} ({sectionItems.length})
              </p>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {sectionItems.map((process) => (
                  <ProcessCard
                    key={process.process_id}
                    process={process}
                    onAction={handleAction}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
