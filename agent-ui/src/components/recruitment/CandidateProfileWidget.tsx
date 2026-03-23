"use client";

import { useRouter } from "next/navigation";

const STAGE_ORDER = [
  "inscrito",
  "triagem",
  "entrevista",
  "tecnico",
  "proposta",
  "contratado",
] as const;

const STAGE_LABELS: Record<string, string> = {
  inscrito: "Inscrito",
  triagem: "Triagem",
  entrevista: "Entrevista",
  tecnico: "Técnico",
  proposta: "Proposta",
  contratado: "Contratado",
  reprovado: "Reprovado",
  desistiu: "Desistiu",
};

const RECOMMENDATION_CONFIG: Record<
  string,
  { label: string; color: string; bg: string }
> = {
  aprovar: {
    label: "Aprovado",
    color: "text-green-400",
    bg: "bg-green-500/10 border-green-500/20",
  },
  reprovar: {
    label: "Reprovado",
    color: "text-red-400",
    bg: "bg-red-500/10 border-red-500/20",
  },
  pendente: {
    label: "Pendente",
    color: "text-yellow-400",
    bg: "bg-yellow-500/10 border-yellow-500/20",
  },
};

export type CandidateProfileWidgetData = {
  candidate_id: string;
  full_name: string;
  email: string;
  phone?: string;
  current_stage: string;
  process_id: string;
  process_title?: string;
  days_in_stage: number;
  applied_at: string;
  screening_recommendation?: string;
  screening_notes?: string;
};

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((n) => n[0])
    .join("")
    .toUpperCase();
}

export function CandidateProfileWidget(data: CandidateProfileWidgetData) {
  const router = useRouter();

  const isInactive =
    data.current_stage === "reprovado" || data.current_stage === "desistiu";

  const currentIndex = STAGE_ORDER.indexOf(
    data.current_stage as (typeof STAGE_ORDER)[number]
  );

  function go(prompt: string) {
    router.push(`/?prompt=${encodeURIComponent(prompt)}`);
  }

  const rec = data.screening_recommendation
    ? RECOMMENDATION_CONFIG[data.screening_recommendation] ??
      RECOMMENDATION_CONFIG["pendente"]
    : null;

  return (
    <div className="mt-2 rounded-xl border border-border bg-background-secondary overflow-hidden w-full">
      {/* Header */}
      <div className="flex items-center gap-4 px-4 py-4 border-b border-border">
        {/* Avatar */}
        <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-base select-none">
          {initials(data.full_name)}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-primary text-sm">
              {data.full_name}
            </h3>
            {rec && (
              <span
                className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${rec.bg} ${rec.color}`}
              >
                {rec.label}
              </span>
            )}
          </div>
          <p className="text-xs text-muted mt-0.5 truncate">{data.email}</p>
          {data.phone && (
            <p className="text-xs text-muted truncate">{data.phone}</p>
          )}
        </div>

        {/* ID badge */}
        <span className="flex-shrink-0 text-[10px] font-mono text-muted/60 bg-background rounded px-1.5 py-0.5 border border-border">
          {data.candidate_id}
        </span>
      </div>

      {/* Stage funnel progress */}
      {!isInactive ? (
        <div className="px-4 py-3 border-b border-border">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted mb-2">
            Progresso no funil
          </p>
          <div className="flex items-center gap-0.5">
            {STAGE_ORDER.map((stage, i) => {
              const isPast = i < currentIndex;
              const isCurrent = i === currentIndex;
              const isFuture = i > currentIndex;
              return (
                <div key={stage} className="flex-1 flex flex-col items-center gap-1">
                  {/* Bar segment */}
                  <div
                    className={`h-1.5 w-full rounded-full transition-colors ${
                      isPast
                        ? "bg-blue-500"
                        : isCurrent
                        ? "bg-blue-400"
                        : "bg-border"
                    }`}
                  />
                  {/* Label */}
                  <span
                    className={`text-[9px] text-center leading-tight ${
                      isCurrent
                        ? "text-blue-400 font-semibold"
                        : isFuture
                        ? "text-muted/40"
                        : "text-muted/60"
                    }`}
                  >
                    {STAGE_LABELS[stage]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="px-4 py-3 border-b border-border">
          <span
            className={`inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg border ${
              data.current_stage === "reprovado"
                ? "bg-red-500/10 border-red-500/20 text-red-400"
                : "bg-gray-500/10 border-gray-500/20 text-gray-400"
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-current" />
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
          <p className="text-[10px] text-muted mt-0.5">etapa atual</p>
        </div>
        <div className="px-3 py-2.5 text-center">
          <p
            className={`text-sm font-bold ${
              data.days_in_stage > 7 ? "text-yellow-400" : "text-primary"
            }`}
          >
            {data.days_in_stage}d
          </p>
          <p className="text-[10px] text-muted mt-0.5">nesta etapa</p>
        </div>
        <div className="px-3 py-2.5 text-center">
          <p className="text-sm font-bold text-primary">{data.applied_at}</p>
          <p className="text-[10px] text-muted mt-0.5">inscrito em</p>
        </div>
      </div>

      {/* Process link */}
      {(data.process_id || data.process_title) && (
        <div className="px-4 py-2.5 border-b border-border flex items-center gap-2">
          <span className="text-xs text-muted">Processo:</span>
          <button
            className="text-xs text-primary hover:underline font-medium"
            onClick={() =>
              go(
                `Me dê um resumo detalhado do processo "${data.process_title ?? data.process_id}" (ID: ${data.process_id}).`
              )
            }
          >
            {data.process_title ?? data.process_id}
          </button>
          <span className="text-[10px] font-mono text-muted/50 ml-auto">
            {data.process_id}
          </span>
        </div>
      )}

      {/* Screening notes */}
      {data.screening_notes && (
        <div className="px-4 py-3 border-b border-border">
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted mb-1.5">
            Notas de triagem
          </p>
          <p className="text-xs text-muted leading-relaxed">{data.screening_notes}</p>
        </div>
      )}

      {/* Quick actions */}
      <div className="px-4 py-3 flex flex-wrap gap-2">
        {!isInactive && (
          <button
            className="text-xs px-3 py-1.5 rounded-lg border border-border bg-background hover:bg-accent text-primary transition-colors font-medium"
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
          className="text-xs px-3 py-1.5 rounded-lg border border-border bg-background hover:bg-accent text-primary transition-colors font-medium"
          onClick={() =>
            go(
              `Agende uma entrevista para o candidato ${data.full_name} (ID: ${data.candidate_id}) no processo (ID: ${data.process_id}).`
            )
          }
        >
          Agendar entrevista
        </button>
        <button
          className="text-xs px-3 py-1.5 rounded-lg border border-border bg-background hover:bg-accent text-primary transition-colors font-medium"
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
            className="text-xs px-3 py-1.5 rounded-lg border border-red-500/20 bg-red-500/5 hover:bg-red-500/10 text-red-400 transition-colors font-medium ml-auto"
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
  );
}
