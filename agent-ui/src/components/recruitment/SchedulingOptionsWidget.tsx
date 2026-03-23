"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export type InterviewerInfo = {
  interviewer_id: string;
  name: string;
  role: string;
  department: string;
};

export type InterviewTypeInfo = {
  interview_type: string;
  label: string;
  description: string;
};

export type SchedulingOptionsWidgetData = {
  __widget: "scheduling_options";
  interviewers: InterviewerInfo[];
  interview_types: InterviewTypeInfo[];
  process_id?: string;
  candidate_id?: string;
  candidate_name?: string;
};

const DEPT_COLOR: Record<string, { bg: string; text: string; dot: string }> = {
  RH:                 { bg: "bg-purple-500/10 border-purple-500/20", text: "text-purple-400", dot: "bg-purple-400" },
  Engenharia:         { bg: "bg-blue-500/10 border-blue-500/20",     text: "text-blue-400",   dot: "bg-blue-400" },
  Produto:            { bg: "bg-orange-500/10 border-orange-500/20", text: "text-orange-400", dot: "bg-orange-400" },
  "Dados & Analytics":{ bg: "bg-cyan-500/10 border-cyan-500/20",     text: "text-cyan-400",   dot: "bg-cyan-400" },
};

const TYPE_COLOR: Record<string, { bg: string; text: string; border: string }> = {
  rh:      { bg: "bg-purple-500/10", text: "text-purple-300", border: "border-purple-500/30" },
  tecnica: { bg: "bg-blue-500/10",   text: "text-blue-300",   border: "border-blue-500/30" },
  cultural:{ bg: "bg-green-500/10",  text: "text-green-300",  border: "border-green-500/30" },
  gestao:  { bg: "bg-orange-500/10", text: "text-orange-300", border: "border-orange-500/30" },
};

function initials(name: string) {
  return name.split(" ").filter(Boolean).slice(0, 2).map((n) => n[0]).join("").toUpperCase();
}

function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="ml-auto flex-shrink-0 text-[10px] font-mono px-1.5 py-0.5 rounded border border-border text-muted hover:text-primary hover:bg-accent transition-colors"
      onClick={() => {
        navigator.clipboard.writeText(value);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
      title="Copiar ID"
    >
      {copied ? "✓" : value}
    </button>
  );
}

export function SchedulingOptionsWidget(data: SchedulingOptionsWidgetData) {
  const router = useRouter();

  function startScheduling(interviewerId: string, interviewerName: string, interviewType: string) {
    const parts = [
      `Quero agendar uma entrevista do tipo "${interviewType}" com ${interviewerName} (ID: ${interviewerId})`,
      data.candidate_name ? `para o candidato ${data.candidate_name}` : "",
      data.candidate_id ? `(ID: ${data.candidate_id})` : "",
      data.process_id ? `no processo ${data.process_id}` : "",
    ].filter(Boolean);
    router.push(`/?prompt=${encodeURIComponent(parts.join(" ") + ". Qual a data e horário?")}`);
  }

  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedInterviewer, setSelectedInterviewer] = useState<string | null>(null);

  const canSchedule = selectedType && selectedInterviewer;
  const interviewer = data.interviewers.find((i) => i.interviewer_id === selectedInterviewer);

  return (
    <div className="mt-2 rounded-xl border border-border bg-background-secondary overflow-hidden w-full">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
        <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-500/15 border border-indigo-500/20 flex items-center justify-center">
          <svg className="w-4 h-4 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-primary">Agendar Entrevista</p>
          <p className="text-xs text-muted">Selecione o tipo e o entrevistador</p>
        </div>
        {data.candidate_name && (
          <div className="ml-auto flex items-center gap-2 bg-background rounded-lg border border-border px-2.5 py-1.5">
            <span className="text-xs text-muted">Candidato:</span>
            <span className="text-xs font-semibold text-primary">{data.candidate_name}</span>
          </div>
        )}
      </div>

      <div className="p-4 space-y-5">
        {/* Interview types */}
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted mb-2.5">
            Tipo de entrevista
          </p>
          <div className="grid grid-cols-2 gap-2">
            {data.interview_types.map((t) => {
              const c = TYPE_COLOR[t.interview_type] ?? { bg: "bg-background", text: "text-primary", border: "border-border" };
              const isSelected = selectedType === t.interview_type;
              return (
                <button
                  key={t.interview_type}
                  onClick={() => setSelectedType(isSelected ? null : t.interview_type)}
                  className={`text-left rounded-lg border p-3 transition-all ${
                    isSelected
                      ? `${c.bg} ${c.border} ring-1 ring-inset ${c.border}`
                      : "border-border bg-background hover:bg-accent"
                  }`}
                >
                  <p className={`text-xs font-semibold ${isSelected ? c.text : "text-primary"}`}>
                    {t.label}
                  </p>
                  <p className="text-[10px] text-muted mt-0.5 leading-snug">{t.description}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Interviewers */}
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-widest text-muted mb-2.5">
            Entrevistadores disponíveis
          </p>
          <div className="space-y-2">
            {data.interviewers.map((i) => {
              const dept = DEPT_COLOR[i.department] ?? { bg: "bg-background border-border", text: "text-muted", dot: "bg-muted" };
              const isSelected = selectedInterviewer === i.interviewer_id;
              return (
                <button
                  key={i.interviewer_id}
                  onClick={() => setSelectedInterviewer(isSelected ? null : i.interviewer_id)}
                  className={`w-full flex items-center gap-3 rounded-lg border px-3 py-2.5 text-left transition-all ${
                    isSelected
                      ? "border-indigo-500/40 bg-indigo-500/8 ring-1 ring-inset ring-indigo-500/20"
                      : "border-border bg-background hover:bg-accent"
                  }`}
                >
                  {/* Avatar */}
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-[11px] font-bold select-none">
                    {initials(i.name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-primary truncate">{i.name}</p>
                    <p className="text-xs text-muted truncate">{i.role}</p>
                  </div>
                  <span className={`flex-shrink-0 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${dept.bg} ${dept.text}`}>
                    {i.department}
                  </span>
                  <CopyButton value={i.interviewer_id} />
                </button>
              );
            })}
          </div>
        </div>

        {/* CTA */}
        <button
          disabled={!canSchedule}
          onClick={() => {
            if (!canSchedule || !interviewer) return;
            const typeLabel = data.interview_types.find((t) => t.interview_type === selectedType)?.label ?? selectedType;
            startScheduling(interviewer.interviewer_id, interviewer.name, typeLabel!);
          }}
          className={`w-full py-2.5 rounded-lg text-sm font-semibold transition-all ${
            canSchedule
              ? "bg-indigo-600 hover:bg-indigo-500 text-white"
              : "bg-background border border-border text-muted cursor-not-allowed"
          }`}
        >
          {canSchedule
            ? `Agendar — ${data.interview_types.find((t) => t.interview_type === selectedType)?.label} com ${interviewer?.name}`
            : "Selecione o tipo e o entrevistador para continuar"}
        </button>
      </div>
    </div>
  );
}
