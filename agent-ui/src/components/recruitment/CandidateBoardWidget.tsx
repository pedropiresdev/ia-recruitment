"use client";

import { useRouter } from "next/navigation";

const STAGE_CONFIG: Record<string, { label: string; color: string; dot: string }> = {
  inscrito:   { label: "Inscritos",    color: "text-blue-400",   dot: "bg-blue-400" },
  triagem:    { label: "Triagem",      color: "text-purple-400", dot: "bg-purple-400" },
  entrevista: { label: "Entrevista",   color: "text-yellow-400", dot: "bg-yellow-400" },
  tecnico:    { label: "Técnico",      color: "text-orange-400", dot: "bg-orange-400" },
  proposta:   { label: "Proposta",     color: "text-cyan-400",   dot: "bg-cyan-400" },
  contratado: { label: "Contratados",  color: "text-green-400",  dot: "bg-green-400" },
  reprovado:  { label: "Reprovados",   color: "text-red-400",    dot: "bg-red-400" },
  desistiu:   { label: "Desistências", color: "text-gray-400",   dot: "bg-gray-400" },
};

const STAGE_ORDER = ["inscrito","triagem","entrevista","tecnico","proposta","contratado","reprovado","desistiu"];

type CandidateItem = {
  candidate_id: string;
  full_name: string;
  days_in_stage: number;
};

type StageGroup = {
  stage_name: string;
  candidates: CandidateItem[];
};

export type CandidateBoardWidgetData = {
  process_id: string;
  job_title: string;
  total_candidates: number;
  stages: StageGroup[];
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

export function CandidateBoardWidget(data: CandidateBoardWidgetData) {
  const router = useRouter();

  const sorted = [...data.stages].sort(
    (a, b) =>
      (STAGE_ORDER.indexOf(a.stage_name) ?? 99) -
      (STAGE_ORDER.indexOf(b.stage_name) ?? 99)
  );

  // Active stages (not rejected/withdrawn) for top metrics
  const activeStages = sorted.filter(
    (s) => s.stage_name !== "reprovado" && s.stage_name !== "desistiu"
  );
  const inactiveStages = sorted.filter(
    (s) => s.stage_name === "reprovado" || s.stage_name === "desistiu"
  );

  function openCandidateChat(candidate: CandidateItem) {
    const prompt = `Me dê o perfil completo do candidato ${candidate.full_name} (ID: ${candidate.candidate_id}) no processo "${data.job_title}" (ID: ${data.process_id}).`;
    router.push(`/?prompt=${encodeURIComponent(prompt)}`);
  }

  function moveStage(candidate: CandidateItem, stageName: string) {
    const stageLabel = STAGE_CONFIG[stageName]?.label ?? stageName;
    const prompt = `Mova o candidato ${candidate.full_name} (ID: ${candidate.candidate_id}) para a etapa "${stageLabel}" no processo "${data.job_title}" (ID: ${data.process_id}).`;
    router.push(`/?prompt=${encodeURIComponent(prompt)}`);
  }

  return (
    <div className="mt-2 rounded-xl border border-border bg-background-secondary overflow-hidden w-full">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border">
        <div>
          <p className="text-sm font-semibold text-primary">{data.job_title}</p>
          <p className="text-xs text-muted mt-0.5">{data.process_id}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">
            {data.total_candidates} candidato{data.total_candidates !== 1 ? "s" : ""}
          </span>
        </div>
      </div>

      {/* Active stages */}
      <div className="p-4 space-y-4">
        {activeStages.map((stage) => {
          const cfg = STAGE_CONFIG[stage.stage_name] ?? {
            label: stage.stage_name,
            color: "text-muted",
            dot: "bg-muted",
          };
          return (
            <div key={stage.stage_name}>
              <div className="flex items-center gap-2 mb-2">
                <span className={`inline-block w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
                <span className={`text-[10px] font-semibold uppercase tracking-widest ${cfg.color}`}>
                  {cfg.label}
                </span>
                <span className="text-[10px] text-muted">({stage.candidates.length})</span>
              </div>
              <div className="grid grid-cols-1 gap-1.5 sm:grid-cols-2">
                {stage.candidates.map((c) => (
                  <div
                    key={c.candidate_id}
                    className="group flex items-center gap-3 rounded-lg border border-border bg-background px-3 py-2 cursor-pointer hover:bg-accent/30 transition-colors"
                    onClick={() => openCandidateChat(c)}
                  >
                    {/* Avatar */}
                    <div className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-white ${cfg.dot}`}>
                      {initials(c.full_name)}
                    </div>
                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-primary truncate">{c.full_name}</p>
                      <p className="text-[10px] text-muted">{c.days_in_stage}d nesta etapa</p>
                    </div>
                    {/* Days badge — highlight if stuck */}
                    {c.days_in_stage > 7 && (
                      <span className="flex-shrink-0 text-[9px] px-1.5 py-0.5 rounded-full bg-yellow-500/15 text-yellow-400 border border-yellow-500/20 font-medium">
                        parado
                      </span>
                    )}
                    {/* Quick move action */}
                    <button
                      className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] px-2 py-1 rounded-md bg-accent text-primary font-medium"
                      onClick={(e) => {
                        e.stopPropagation();
                        moveStage(c, stage.stage_name);
                      }}
                    >
                      Mover
                    </button>
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {/* Inactive stages (rejected/withdrawn) — collapsed section */}
        {inactiveStages.some((s) => s.candidates.length > 0) && (
          <details className="group">
            <summary className="cursor-pointer text-[10px] font-semibold uppercase tracking-widest text-muted list-none flex items-center gap-1.5 select-none hover:text-primary transition-colors">
              <svg className="w-3 h-3 transition-transform group-open:rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
              Inativos (
              {inactiveStages.reduce((acc, s) => acc + s.candidates.length, 0)})
            </summary>
            <div className="mt-3 space-y-3">
              {inactiveStages.map((stage) => {
                if (stage.candidates.length === 0) return null;
                const cfg = STAGE_CONFIG[stage.stage_name] ?? { label: stage.stage_name, color: "text-muted", dot: "bg-muted" };
                return (
                  <div key={stage.stage_name}>
                    <p className={`text-[10px] font-semibold uppercase tracking-widest mb-1.5 ${cfg.color}`}>
                      {cfg.label} ({stage.candidates.length})
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {stage.candidates.map((c) => (
                        <span
                          key={c.candidate_id}
                          className="text-xs px-2 py-0.5 rounded-full bg-background border border-border text-muted"
                        >
                          {c.full_name}
                        </span>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
