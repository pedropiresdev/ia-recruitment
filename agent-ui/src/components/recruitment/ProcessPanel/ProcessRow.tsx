"use client";

import type { RecruitmentProcess } from "@/types/recruitment";
import { SLABadge } from "./SLABadge";

const STATUS_LABELS: Record<RecruitmentProcess["status"], string> = {
  em_aberto: "Em aberto",
  em_andamento: "Em andamento",
  suspenso: "Suspenso",
  encerrado: "Encerrado",
};

type ProcessRowProps = {
  process: RecruitmentProcess;
  onRowClick: (prompt: string) => void;
};

export function ProcessRow({ process, onRowClick }: ProcessRowProps) {
  const prompt = `Me dê um resumo detalhado do processo seletivo "${process.job_title}" (ID: ${process.process_id}) e o que precisa ser feito para regularizar o SLA.`;

  return (
    <tr
      className="cursor-pointer hover:bg-accent/50 transition-colors border-b border-border"
      onClick={() => onRowClick(prompt)}
    >
      <td className="px-4 py-3 font-medium text-primary">{process.job_title}</td>
      <td className="px-4 py-3 text-muted">{process.department}</td>
      <td className="px-4 py-3 text-muted">{process.recruiter_name}</td>
      <td className="px-4 py-3 text-muted">{STATUS_LABELS[process.status]}</td>
      <td className="px-4 py-3">
        <SLABadge status={process.sla_status} />
      </td>
      <td className="px-4 py-3 text-muted text-sm">
        {process.open_candidates_count} candidatos
      </td>
      <td className="px-4 py-3 text-muted text-sm">
        {process.days_since_last_update}d atrás
      </td>
    </tr>
  );
}
