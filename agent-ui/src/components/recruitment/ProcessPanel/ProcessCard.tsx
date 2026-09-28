'use client'

import type { RecruitmentProcess } from '@/types/recruitment'
import { SLABadge } from './SLABadge'

const STATUS_LABELS: Record<RecruitmentProcess['status'], string> = {
  em_aberto: 'Em aberto',
  em_andamento: 'Em andamento',
  suspenso: 'Suspenso',
  encerrado: 'Encerrado'
}

const STATUS_DOT: Record<RecruitmentProcess['status'], string> = {
  em_aberto: 'bg-blue-400',
  em_andamento: 'bg-green-400',
  suspenso: 'bg-gray-400',
  encerrado: 'bg-zinc-500'
}

const SLA_BORDER: Record<RecruitmentProcess['sla_status'], string> = {
  no_prazo: 'border-l-green-500',
  em_risco: 'border-l-yellow-500',
  em_atraso: 'border-l-red-500'
}

type ProcessCardProps = {
  process: RecruitmentProcess
  onAction: (prompt: string) => void
}

export function ProcessCard({ process, onAction }: ProcessCardProps) {
  const detailPrompt = `Me dê um resumo detalhado do processo seletivo "${process.job_title}" (ID: ${process.process_id}) e o que precisa ser feito para regularizar o SLA.`
  const cobrancaPrompt = `Rascunhe uma mensagem de cobrança para o gestor responsável pelo processo "${process.job_title}" (ID: ${process.process_id}).`
  const candidatosPrompt = `Quais candidatos estão aguardando retorno no processo "${process.job_title}" (ID: ${process.process_id})?`

  return (
    <div
      className={`group relative rounded-xl border border-l-4 border-border ${SLA_BORDER[process.sla_status]} cursor-pointer bg-background-secondary p-4 transition-all duration-200 hover:bg-accent/20 hover:shadow-md`}
      onClick={() => onAction(detailPrompt)}
    >
      {/* Header */}
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-sm font-semibold leading-tight text-primary">
            {process.job_title}
          </h3>
          <p className="mt-0.5 truncate text-xs text-muted">
            {process.department}
          </p>
        </div>
        <SLABadge status={process.sla_status} />
      </div>

      {/* Meta */}
      <div className="mb-3 flex items-center gap-1.5 text-xs text-muted">
        <span
          className={`inline-block h-1.5 w-1.5 flex-shrink-0 rounded-full ${STATUS_DOT[process.status]}`}
        />
        <span>{STATUS_LABELS[process.status]}</span>
        <span className="text-border">·</span>
        <span>{process.recruiter_name}</span>
      </div>

      {/* Stats */}
      <div className="mb-3 grid grid-cols-2 gap-2">
        <div className="rounded-lg bg-background px-2 py-1.5 text-center">
          <p className="text-sm font-semibold text-primary">
            {process.open_candidates_count}
          </p>
          <p className="text-xs text-muted">candidatos</p>
        </div>
        <div className="rounded-lg bg-background px-2 py-1.5 text-center">
          <p className="text-sm font-semibold text-primary">
            {process.days_since_last_update}d
          </p>
          <p className="text-xs text-muted">sem atualização</p>
        </div>
      </div>

      {/* Deadline */}
      {process.sla_deadline_date && (
        <p className="mb-3 text-xs text-muted">
          Prazo:{' '}
          <span className="font-medium text-primary">
            {process.sla_deadline_date}
          </span>
        </p>
      )}

      {/* Actions — visible on hover */}
      <div className="flex gap-1.5 opacity-0 transition-opacity duration-150 group-hover:opacity-100">
        <button
          className="flex-1 rounded-md bg-accent px-2 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent/80"
          onClick={(e) => {
            e.stopPropagation()
            onAction(cobrancaPrompt)
          }}
        >
          Cobrar gestor
        </button>
        <button
          className="flex-1 rounded-md bg-accent px-2 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent/80"
          onClick={(e) => {
            e.stopPropagation()
            onAction(candidatosPrompt)
          }}
        >
          Ver candidatos
        </button>
      </div>

      {/* Click hint */}
      <p className="mt-2 text-center text-xs text-muted/50 group-hover:hidden">
        Clique para detalhes
      </p>
    </div>
  )
}
