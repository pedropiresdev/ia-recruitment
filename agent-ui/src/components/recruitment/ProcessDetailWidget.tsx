'use client'

import { useRouter } from 'next/navigation'
import type {
  ProcessStatus,
  SLAStatus,
  QuickAction,
  ProcessTimelineEvent
} from '@/types/recruitment'
import { SLABadge } from './ProcessPanel/SLABadge'

const STATUS_LABELS: Record<ProcessStatus, string> = {
  em_aberto: 'Em aberto',
  em_andamento: 'Em andamento',
  suspenso: 'Suspenso',
  encerrado: 'Encerrado'
}

const STATUS_DOT: Record<ProcessStatus, string> = {
  em_aberto: 'bg-blue-400',
  em_andamento: 'bg-green-400',
  suspenso: 'bg-gray-400',
  encerrado: 'bg-zinc-500'
}

export type ProcessDetailWidgetData = {
  process_id: string
  job_title: string
  department: string
  recruiter_name: string
  status: ProcessStatus
  sla_status: SLAStatus
  sla_deadline_date: string
  days_overdue: number
  days_since_last_update: number
  open_candidates_count: number
  bottleneck_description: string
  timeline: ProcessTimelineEvent[]
  recommended_actions: QuickAction[]
}

export function ProcessDetailWidget(data: ProcessDetailWidgetData) {
  const router = useRouter()

  function handleAction(prompt: string) {
    router.push(`/?prompt=${encodeURIComponent(prompt)}`)
  }

  const isOverdue = data.sla_status === 'em_atraso'
  const isAtRisk = data.sla_status === 'em_risco'

  const recentTimeline = [...data.timeline]
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 5)

  return (
    <div className="mt-2 w-full overflow-hidden rounded-xl border border-border bg-background-secondary">
      {/* Header */}
      <div
        className={`border-b border-border px-4 py-3 ${
          isOverdue
            ? 'border-l-4 border-l-red-500 bg-red-500/5'
            : isAtRisk
              ? 'border-l-4 border-l-yellow-500 bg-yellow-500/5'
              : 'border-l-4 border-l-green-500'
        }`}
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-primary">
              {data.job_title}
            </h3>
            <p className="mt-0.5 text-xs text-muted">
              {data.department} · {data.recruiter_name}
            </p>
          </div>
          <SLABadge status={data.sla_status} />
        </div>
        <div className="mt-2 flex items-center gap-1.5 text-xs text-muted">
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_DOT[data.status]}`}
          />
          <span>{STATUS_LABELS[data.status]}</span>
          <span className="text-border">·</span>
          <span className="font-mono text-muted/70">{data.process_id}</span>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-3 divide-x divide-border border-b border-border">
        <div className="px-4 py-3 text-center">
          <p
            className={`text-xl font-bold ${
              isOverdue
                ? 'text-red-400'
                : isAtRisk
                  ? 'text-yellow-400'
                  : 'text-primary'
            }`}
          >
            {isOverdue ? `${data.days_overdue}d` : data.sla_deadline_date}
          </p>
          <p className="mt-0.5 text-[10px] text-muted">
            {isOverdue ? 'em atraso' : 'prazo'}
          </p>
        </div>
        <div className="px-4 py-3 text-center">
          <p className="text-xl font-bold text-primary">
            {data.open_candidates_count}
          </p>
          <p className="mt-0.5 text-[10px] text-muted">candidatos</p>
        </div>
        <div className="px-4 py-3 text-center">
          <p
            className={`text-xl font-bold ${
              data.days_since_last_update > 7
                ? 'text-yellow-400'
                : 'text-primary'
            }`}
          >
            {data.days_since_last_update}d
          </p>
          <p className="mt-0.5 text-[10px] text-muted">sem atualização</p>
        </div>
      </div>

      {/* Bottleneck */}
      {data.bottleneck_description && (
        <div
          className={`mx-4 mt-4 rounded-lg px-3 py-2.5 text-xs ${
            isOverdue
              ? 'border border-red-500/20 bg-red-500/10 text-red-300'
              : isAtRisk
                ? 'border border-yellow-500/20 bg-yellow-500/10 text-yellow-300'
                : 'border border-border bg-background text-muted'
          }`}
        >
          <p className="mb-0.5 text-[10px] font-semibold uppercase tracking-wide opacity-70">
            Gargalo identificado
          </p>
          <p>{data.bottleneck_description}</p>
        </div>
      )}

      {/* Timeline */}
      {recentTimeline.length > 0 && (
        <div className="mt-4 px-4">
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted">
            Histórico recente
          </p>
          <div className="space-y-0">
            {recentTimeline.map((event, i) => (
              <div key={i} className="relative flex gap-3 pb-3 text-xs">
                {/* Timeline line */}
                {i < recentTimeline.length - 1 && (
                  <div className="absolute bottom-0 left-[5px] top-3 w-px bg-border" />
                )}
                <div className="relative z-10 mt-0.5 h-2.5 w-2.5 flex-shrink-0 rounded-full border-2 border-background-secondary bg-border" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-baseline gap-1.5">
                    <span className="font-medium text-primary">
                      {event.stage}
                    </span>
                    <span className="text-muted">·</span>
                    <span className="text-muted">{event.actor}</span>
                    <span className="ml-auto flex-shrink-0 text-muted/60">
                      {event.date}
                    </span>
                  </div>
                  {event.notes && (
                    <p className="mt-0.5 truncate text-muted">{event.notes}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick actions */}
      {data.recommended_actions.length > 0 && (
        <div className="mt-2 px-4 pb-4">
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted">
            Ações rápidas
          </p>
          <div className="flex flex-wrap gap-2">
            {data.recommended_actions.map((action, i) => (
              <button
                key={i}
                onClick={() => handleAction(action.prompt)}
                className="rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent"
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
