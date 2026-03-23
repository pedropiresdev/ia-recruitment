"use client";

import type { RecruitmentProcess } from "@/types/recruitment";
import { SLABadge } from "./SLABadge";

const STATUS_LABELS: Record<RecruitmentProcess["status"], string> = {
  em_aberto: "Em aberto",
  em_andamento: "Em andamento",
  suspenso: "Suspenso",
  encerrado: "Encerrado",
};

const STATUS_DOT: Record<RecruitmentProcess["status"], string> = {
  em_aberto: "bg-blue-400",
  em_andamento: "bg-green-400",
  suspenso: "bg-gray-400",
  encerrado: "bg-zinc-500",
};

const SLA_BORDER: Record<RecruitmentProcess["sla_status"], string> = {
  no_prazo: "border-l-green-500",
  em_risco: "border-l-yellow-500",
  em_atraso: "border-l-red-500",
};

type ProcessCardProps = {
  process: RecruitmentProcess;
  onAction: (prompt: string) => void;
};

export function ProcessCard({ process, onAction }: ProcessCardProps) {
  const detailPrompt = `Me dê um resumo detalhado do processo seletivo "${process.job_title}" (ID: ${process.process_id}) e o que precisa ser feito para regularizar o SLA.`;
  const cobrancaPrompt = `Rascunhe uma mensagem de cobrança para o gestor responsável pelo processo "${process.job_title}" (ID: ${process.process_id}).`;
  const candidatosPrompt = `Quais candidatos estão aguardando retorno no processo "${process.job_title}" (ID: ${process.process_id})?`;

  return (
    <div
      className={`group relative rounded-xl border border-border border-l-4 ${SLA_BORDER[process.sla_status]} bg-background-secondary p-4 cursor-pointer hover:shadow-md hover:bg-accent/20 transition-all duration-200`}
      onClick={() => onAction(detailPrompt)}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-primary text-sm leading-tight truncate">
            {process.job_title}
          </h3>
          <p className="text-xs text-muted mt-0.5 truncate">{process.department}</p>
        </div>
        <SLABadge status={process.sla_status} />
      </div>

      {/* Meta */}
      <div className="flex items-center gap-1.5 text-xs text-muted mb-3">
        <span
          className={`inline-block w-1.5 h-1.5 rounded-full flex-shrink-0 ${STATUS_DOT[process.status]}`}
        />
        <span>{STATUS_LABELS[process.status]}</span>
        <span className="text-border">·</span>
        <span>{process.recruiter_name}</span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="rounded-lg bg-background px-2 py-1.5 text-center">
          <p className="text-sm font-semibold text-primary">{process.open_candidates_count}</p>
          <p className="text-xs text-muted">candidatos</p>
        </div>
        <div className="rounded-lg bg-background px-2 py-1.5 text-center">
          <p className="text-sm font-semibold text-primary">{process.days_since_last_update}d</p>
          <p className="text-xs text-muted">sem atualização</p>
        </div>
      </div>

      {/* Deadline */}
      {process.sla_deadline_date && (
        <p className="text-xs text-muted mb-3">
          Prazo:{" "}
          <span className="text-primary font-medium">{process.sla_deadline_date}</span>
        </p>
      )}

      {/* Actions — visible on hover */}
      <div className="flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
        <button
          className="flex-1 text-xs px-2 py-1.5 rounded-md bg-accent hover:bg-accent/80 text-primary transition-colors font-medium"
          onClick={(e) => {
            e.stopPropagation();
            onAction(cobrancaPrompt);
          }}
        >
          Cobrar gestor
        </button>
        <button
          className="flex-1 text-xs px-2 py-1.5 rounded-md bg-accent hover:bg-accent/80 text-primary transition-colors font-medium"
          onClick={(e) => {
            e.stopPropagation();
            onAction(candidatosPrompt);
          }}
        >
          Ver candidatos
        </button>
      </div>

      {/* Click hint */}
      <p className="text-xs text-muted/50 mt-2 group-hover:hidden text-center">
        Clique para detalhes
      </p>
    </div>
  );
}
