'use client'

import { useRouter } from 'next/navigation'

const TYPE_CONFIG: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  tecnica: {
    label: 'Técnica',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10 border-blue-500/20'
  },
  cultural: {
    label: 'Cultural',
    color: 'text-purple-400',
    bg: 'bg-purple-500/10 border-purple-500/20'
  },
  gestao: {
    label: 'Gestão',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10 border-orange-500/20'
  },
  rh: {
    label: 'RH',
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10 border-cyan-500/20'
  }
}

const STATUS_CONFIG: Record<
  string,
  { label: string; color: string; dot: string }
> = {
  agendada: { label: 'Agendada', color: 'text-green-400', dot: 'bg-green-400' },
  cancelada: { label: 'Cancelada', color: 'text-red-400', dot: 'bg-red-400' },
  realizada: { label: 'Realizada', color: 'text-muted', dot: 'bg-muted' }
}

export type InterviewItem = {
  interview_id: string
  candidate_id: string
  candidate_name: string
  process_id: string
  interviewer_id: string
  interview_type: string
  scheduled_datetime: string
  duration_minutes: number
  status: string
  notes?: string
  cancellation_reason?: string
  reschedule_reason?: string
}

export type InterviewWidgetData =
  | {
      __widget: 'interview_list'
      process_id: string
      job_title?: string
      interviews: InterviewItem[]
    }
  | { __widget: 'interview_card'; interview: InterviewItem; job_title?: string }

function initials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

function formatDateTime(iso: string) {
  try {
    const d = new Date(iso)
    return {
      date: d.toLocaleDateString('pt-BR', {
        weekday: 'short',
        day: '2-digit',
        month: 'short'
      }),
      time: d.toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  } catch {
    return { date: iso, time: '' }
  }
}

function InterviewCard({
  interview,
  jobTitle,
  onAction,
  compact = false
}: {
  interview: InterviewItem
  jobTitle?: string
  onAction: (prompt: string) => void
  compact?: boolean
}) {
  const typeCfg = TYPE_CONFIG[interview.interview_type] ?? {
    label: interview.interview_type,
    color: 'text-muted',
    bg: 'bg-background border-border'
  }
  const statusCfg = STATUS_CONFIG[interview.status] ?? {
    label: interview.status,
    color: 'text-muted',
    dot: 'bg-muted'
  }
  const { date, time } = formatDateTime(interview.scheduled_datetime)
  const isActive = interview.status === 'agendada'

  return (
    <div
      className={`overflow-hidden rounded-xl border border-border bg-background ${
        isActive
          ? 'border-l-4 border-l-green-500'
          : interview.status === 'cancelada'
            ? 'border-l-4 border-l-red-500/50 opacity-70'
            : 'border-l-4 border-l-border'
      }`}
    >
      {/* Card header */}
      <div className="flex items-center gap-3 border-b border-border px-4 py-3">
        {/* Avatar */}
        <div className="flex h-8 w-8 flex-shrink-0 select-none items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-xs font-bold text-white">
          {initials(interview.candidate_name)}
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-primary">
            {interview.candidate_name}
          </p>
          {jobTitle && (
            <p className="truncate text-xs text-muted">{jobTitle}</p>
          )}
        </div>
        {/* Type badge */}
        <span
          className={`flex-shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${typeCfg.bg} ${typeCfg.color}`}
        >
          {typeCfg.label}
        </span>
      </div>

      {/* Datetime + duration row */}
      <div className="flex items-center gap-4 border-b border-border px-4 py-3">
        <div className="flex flex-1 items-center gap-2">
          {/* Calendar icon */}
          <div className="flex h-9 w-9 flex-shrink-0 flex-col items-center justify-center rounded-lg border border-border bg-background-secondary">
            <span className="text-[9px] uppercase leading-none text-muted">
              {date.split(',')[0]}
            </span>
            <span className="text-sm font-bold leading-tight text-primary">
              {date.split(',')[1]?.trim().split(' ')[0]}
            </span>
          </div>
          <div>
            <p className="text-sm font-semibold text-primary">{time}</p>
            <p className="text-xs text-muted">
              {date.split(',').slice(1).join(',').trim()}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm font-semibold text-primary">
            {interview.duration_minutes}min
          </p>
          <p className="text-xs text-muted">duração</p>
        </div>
      </div>

      {/* Status + ID row */}
      <div className="flex items-center gap-2 border-b border-border px-4 py-2">
        <span
          className={`inline-block h-1.5 w-1.5 rounded-full ${statusCfg.dot}`}
        />
        <span className={`text-xs font-medium ${statusCfg.color}`}>
          {statusCfg.label}
        </span>
        <span className="ml-auto font-mono text-[10px] text-muted/50">
          {interview.interview_id}
        </span>
      </div>

      {/* Reason/notes */}
      {interview.cancellation_reason && (
        <div className="border-b border-border bg-red-500/5 px-4 py-2">
          <p className="mb-0.5 text-[10px] font-semibold uppercase tracking-wide text-red-400">
            Motivo do cancelamento
          </p>
          <p className="text-xs text-muted">{interview.cancellation_reason}</p>
        </div>
      )}
      {interview.reschedule_reason && (
        <div className="border-b border-border bg-yellow-500/5 px-4 py-2">
          <p className="mb-0.5 text-[10px] font-semibold uppercase tracking-wide text-yellow-400">
            Motivo da remarcação
          </p>
          <p className="text-xs text-muted">{interview.reschedule_reason}</p>
        </div>
      )}
      {interview.notes && !compact && (
        <div className="border-b border-border px-4 py-2">
          <p className="mb-0.5 text-[10px] font-semibold uppercase tracking-wide text-muted">
            Observações
          </p>
          <p className="text-xs text-muted">{interview.notes}</p>
        </div>
      )}

      {/* Actions */}
      {isActive && (
        <div className="flex gap-2 px-4 py-2.5">
          <button
            className="flex-1 rounded-lg border border-border bg-background-secondary px-2 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent"
            onClick={() =>
              onAction(
                `Remarque a entrevista ${interview.interview_id} do candidato ${interview.candidate_name}. Qual nova data e motivo?`
              )
            }
          >
            Remarcar
          </button>
          <button
            className="flex-1 rounded-lg border border-red-500/20 bg-red-500/5 px-2 py-1.5 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/10"
            onClick={() =>
              onAction(
                `Cancele a entrevista ${interview.interview_id} do candidato ${interview.candidate_name}. Qual o motivo do cancelamento?`
              )
            }
          >
            Cancelar
          </button>
        </div>
      )}
    </div>
  )
}

export function InterviewWidget(data: InterviewWidgetData) {
  const router = useRouter()

  function go(prompt: string) {
    router.push(`/?prompt=${encodeURIComponent(prompt)}`)
  }

  if (data.__widget === 'interview_card') {
    return (
      <div className="mt-2 w-full max-w-sm">
        <InterviewCard
          interview={data.interview}
          jobTitle={data.job_title}
          onAction={go}
        />
      </div>
    )
  }

  // interview_list
  const { interviews, job_title, process_id } = data
  const agendadas = interviews.filter((i) => i.status === 'agendada')
  const outras = interviews.filter((i) => i.status !== 'agendada')

  return (
    <div className="mt-2 w-full overflow-hidden rounded-xl border border-border bg-background-secondary">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div>
          <p className="text-sm font-semibold text-primary">
            {job_title ? `Entrevistas — ${job_title}` : 'Entrevistas'}
          </p>
          {process_id && (
            <p className="mt-0.5 text-xs text-muted">{process_id}</p>
          )}
        </div>
        <div className="flex items-center gap-3 text-xs text-muted">
          {agendadas.length > 0 && (
            <span className="flex items-center gap-1">
              <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
              {agendadas.length} agendada{agendadas.length !== 1 ? 's' : ''}
            </span>
          )}
          {outras.length > 0 && (
            <span className="text-muted/60">
              {outras.length} encerrada{outras.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      <div className="space-y-4 p-4">
        {/* Agendadas */}
        {agendadas.length > 0 && (
          <div>
            <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-green-400">
              Agendadas ({agendadas.length})
            </p>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {agendadas.map((i) => (
                <InterviewCard
                  key={i.interview_id}
                  interview={i}
                  jobTitle={job_title}
                  onAction={go}
                  compact
                />
              ))}
            </div>
          </div>
        )}

        {/* Encerradas */}
        {outras.length > 0 && (
          <details className="group">
            <summary className="flex cursor-pointer select-none list-none items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted transition-colors hover:text-primary">
              <svg
                className="h-3 w-3 transition-transform group-open:rotate-90"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 5l7 7-7 7"
                />
              </svg>
              Encerradas ({outras.length})
            </summary>
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
              {outras.map((i) => (
                <InterviewCard
                  key={i.interview_id}
                  interview={i}
                  jobTitle={job_title}
                  onAction={go}
                  compact
                />
              ))}
            </div>
          </details>
        )}

        {interviews.length === 0 && (
          <p className="py-4 text-center text-xs text-muted">
            Nenhuma entrevista encontrada.
          </p>
        )}
      </div>
    </div>
  )
}
