'use client'

import { useRouter } from 'next/navigation'

const STAGE_ORDER = [
  'inscrito',
  'triagem',
  'entrevista',
  'tecnico',
  'proposta',
  'contratado'
] as const

const STAGE_LABELS: Record<string, string> = {
  inscrito: 'Inscrito',
  triagem: 'Triagem',
  entrevista: 'Entrevista',
  tecnico: 'Técnico',
  proposta: 'Proposta',
  contratado: 'Contratado',
  reprovado: 'Reprovado',
  desistiu: 'Desistiu'
}

const RECOMMENDATION_CONFIG: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  aprovar: {
    label: 'Aprovado',
    color: 'text-green-400',
    bg: 'bg-green-500/10 border-green-500/20'
  },
  reprovar: {
    label: 'Reprovado',
    color: 'text-red-400',
    bg: 'bg-red-500/10 border-red-500/20'
  },
  pendente: {
    label: 'Pendente',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10 border-yellow-500/20'
  }
}

export type CandidateProfileWidgetData = {
  candidate_id: string
  full_name: string
  email: string
  phone?: string
  current_stage: string
  process_id: string
  process_title?: string
  days_in_stage: number
  applied_at: string
  screening_recommendation?: string
  screening_notes?: string
}

function initials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase()
}

export function CandidateProfileWidget(data: CandidateProfileWidgetData) {
  const router = useRouter()

  const isInactive =
    data.current_stage === 'reprovado' || data.current_stage === 'desistiu'

  const currentIndex = STAGE_ORDER.indexOf(
    data.current_stage as (typeof STAGE_ORDER)[number]
  )

  function go(prompt: string) {
    router.push(`/?prompt=${encodeURIComponent(prompt)}`)
  }

  const rec = data.screening_recommendation
    ? (RECOMMENDATION_CONFIG[data.screening_recommendation] ??
      RECOMMENDATION_CONFIG['pendente'])
    : null

  return (
    <div className="mt-2 w-full overflow-hidden rounded-xl border border-border bg-background-secondary">
      {/* Header */}
      <div className="flex items-center gap-4 border-b border-border px-4 py-4">
        {/* Avatar */}
        <div className="flex h-12 w-12 flex-shrink-0 select-none items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-purple-600 text-base font-bold text-white">
          {initials(data.full_name)}
        </div>

        {/* Info */}
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold text-primary">
              {data.full_name}
            </h3>
            {rec && (
              <span
                className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold ${rec.bg} ${rec.color}`}
              >
                {rec.label}
              </span>
            )}
          </div>
          <p className="mt-0.5 truncate text-xs text-muted">{data.email}</p>
          {data.phone && (
            <p className="truncate text-xs text-muted">{data.phone}</p>
          )}
        </div>

        {/* ID badge */}
        <span className="flex-shrink-0 rounded border border-border bg-background px-1.5 py-0.5 font-mono text-[10px] text-muted/60">
          {data.candidate_id}
        </span>
      </div>

      {/* Stage funnel progress */}
      {!isInactive ? (
        <div className="border-b border-border px-4 py-3">
          <p className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted">
            Progresso no funil
          </p>
          <div className="flex items-center gap-0.5">
            {STAGE_ORDER.map((stage, i) => {
              const isPast = i < currentIndex
              const isCurrent = i === currentIndex
              const isFuture = i > currentIndex
              return (
                <div
                  key={stage}
                  className="flex flex-1 flex-col items-center gap-1"
                >
                  {/* Bar segment */}
                  <div
                    className={`h-1.5 w-full rounded-full transition-colors ${
                      isPast
                        ? 'bg-blue-500'
                        : isCurrent
                          ? 'bg-blue-400'
                          : 'bg-border'
                    }`}
                  />
                  {/* Label */}
                  <span
                    className={`text-center text-[9px] leading-tight ${
                      isCurrent
                        ? 'font-semibold text-blue-400'
                        : isFuture
                          ? 'text-muted/40'
                          : 'text-muted/60'
                    }`}
                  >
                    {STAGE_LABELS[stage]}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      ) : (
        <div className="border-b border-border px-4 py-3">
          <span
            className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium ${
              data.current_stage === 'reprovado'
                ? 'border-red-500/20 bg-red-500/10 text-red-400'
                : 'border-gray-500/20 bg-gray-500/10 text-gray-400'
            }`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-current" />
            {STAGE_LABELS[data.current_stage]}
          </span>
        </div>
      )}

      {/* Meta row */}
      <div className="grid grid-cols-3 divide-x divide-border border-b border-border">
        <div className="px-3 py-2.5 text-center">
          <p className="text-sm font-bold text-primary">
            {STAGE_LABELS[data.current_stage] ?? data.current_stage}
          </p>
          <p className="mt-0.5 text-[10px] text-muted">etapa atual</p>
        </div>
        <div className="px-3 py-2.5 text-center">
          <p
            className={`text-sm font-bold ${
              data.days_in_stage > 7 ? 'text-yellow-400' : 'text-primary'
            }`}
          >
            {data.days_in_stage}d
          </p>
          <p className="mt-0.5 text-[10px] text-muted">nesta etapa</p>
        </div>
        <div className="px-3 py-2.5 text-center">
          <p className="text-sm font-bold text-primary">{data.applied_at}</p>
          <p className="mt-0.5 text-[10px] text-muted">inscrito em</p>
        </div>
      </div>

      {/* Process link */}
      {(data.process_id || data.process_title) && (
        <div className="flex items-center gap-2 border-b border-border px-4 py-2.5">
          <span className="text-xs text-muted">Processo:</span>
          <button
            className="text-xs font-medium text-primary hover:underline"
            onClick={() =>
              go(
                `Me dê um resumo detalhado do processo "${data.process_title ?? data.process_id}" (ID: ${data.process_id}).`
              )
            }
          >
            {data.process_title ?? data.process_id}
          </button>
          <span className="ml-auto font-mono text-[10px] text-muted/50">
            {data.process_id}
          </span>
        </div>
      )}

      {/* Screening notes */}
      {data.screening_notes && (
        <div className="border-b border-border px-4 py-3">
          <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted">
            Notas de triagem
          </p>
          <p className="text-xs leading-relaxed text-muted">
            {data.screening_notes}
          </p>
        </div>
      )}

      {/* Quick actions */}
      <div className="flex flex-wrap gap-2 px-4 py-3">
        {!isInactive && (
          <button
            className="rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent"
            onClick={() =>
              go(
                `Mova o candidato ${data.full_name} (ID: ${data.candidate_id}) para a próxima etapa no processo (ID: ${data.process_id}).`
              )
            }
          >
            Avançar etapa
          </button>
        )}
        <button
          className="rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent"
          onClick={() =>
            go(
              `Agende uma entrevista para o candidato ${data.full_name} (ID: ${data.candidate_id}) no processo (ID: ${data.process_id}).`
            )
          }
        >
          Agendar entrevista
        </button>
        <button
          className="rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-medium text-primary transition-colors hover:bg-accent"
          onClick={() =>
            go(
              `Realize a triagem do candidato ${data.full_name} (ID: ${data.candidate_id}) no processo (ID: ${data.process_id}).`
            )
          }
        >
          Triagem
        </button>
        {!isInactive && (
          <button
            className="ml-auto rounded-lg border border-red-500/20 bg-red-500/5 px-3 py-1.5 text-xs font-medium text-red-400 transition-colors hover:bg-red-500/10"
            onClick={() =>
              go(
                `Reprove o candidato ${data.full_name} (ID: ${data.candidate_id}) do processo (ID: ${data.process_id}).`
              )
            }
          >
            Reprovar
          </button>
        )}
      </div>
    </div>
  )
}
