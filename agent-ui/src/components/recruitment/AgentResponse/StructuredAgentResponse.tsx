"use client";

import type { ProcessDetail } from "@/types/recruitment";
import { QuickActionBar } from "../ProcessPanel/QuickActionBar";
import { SLABadge } from "../ProcessPanel/SLABadge";

type StructuredAgentResponseProps = {
  detail: ProcessDetail;
  onAction: (prompt: string) => void;
};

export function StructuredAgentResponse({
  detail,
  onAction,
}: StructuredAgentResponseProps) {
  return (
    <div className="space-y-4 rounded-xl border border-border bg-background-secondary p-4 mt-2">
      {/* Cabeçalho */}
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-primary">{detail.job_title}</h3>
        <SLABadge status={detail.sla_status} />
      </div>

      {/* Bloco 1 obrigatório: Gargalo atual identificado */}
      <div className="rounded-lg bg-background p-3">
        <p className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">
          Gargalo atual
        </p>
        <p className="text-sm text-primary">{detail.bottleneck_description}</p>
        {detail.days_overdue > 0 && (
          <p className="mt-1.5 text-sm font-medium text-red-400">
            {detail.days_overdue} dia{detail.days_overdue !== 1 ? "s" : ""} de atraso no SLA
          </p>
        )}
      </div>

      {/* Bloco 2 obrigatório: Próximas ações recomendadas */}
      <div>
        <p className="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
          Próximas ações recomendadas
        </p>
        <ul className="space-y-1">
          {detail.recommended_actions.map((action) => (
            <li
              key={action.label}
              className="flex items-start gap-2 text-sm text-primary"
            >
              <span className="mt-0.5 text-muted">→</span>
              {action.label}
            </li>
          ))}
        </ul>
      </div>

      {/* Bloco 3 obrigatório: Quick actions clicáveis */}
      <div className="border-t border-border pt-3">
        <p className="text-xs font-semibold text-muted uppercase tracking-wide mb-2">
          Ações rápidas
        </p>
        <QuickActionBar actions={detail.recommended_actions} onAction={onAction} />
      </div>
    </div>
  );
}
