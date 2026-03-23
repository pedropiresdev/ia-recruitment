"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import type { RecruitmentProcess, SLAStatus } from "@/types/recruitment";
import { ProcessCard } from "@/components/recruitment/ProcessPanel/ProcessCard";
import { SLABadge } from "@/components/recruitment/ProcessPanel/SLABadge";

type SLAFilter = SLAStatus | "todos";

const SLA_SECTIONS: { key: SLAFilter; label: string; color: string }[] = [
  { key: "em_atraso", label: "SLA Vencido", color: "text-red-400 border-red-500/20 bg-red-500/5" },
  { key: "em_risco", label: "Em Risco", color: "text-yellow-400 border-yellow-500/20 bg-yellow-500/5" },
  { key: "no_prazo", label: "No Prazo", color: "text-green-400 border-green-500/20 bg-green-500/5" },
];

export default function ProcessosPage() {
  const router = useRouter();
  const [processes, setProcesses] = useState<RecruitmentProcess[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [slaFilter, setSlaFilter] = useState<SLAFilter>("todos");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/processes")
      .then((r) => r.json())
      .then((data) => {
        setProcesses(data.processes ?? []);
        setLoading(false);
      })
      .catch(() => {
        setError("Não foi possível conectar ao servidor. Verifique se o AgentOS está rodando.");
        setLoading(false);
      });
  }, []);

  function handleAction(prompt: string) {
    router.push(`/?prompt=${encodeURIComponent(prompt)}`);
  }

  const filtered = processes.filter((p) => {
    const matchSLA = slaFilter === "todos" || p.sla_status === slaFilter;
    const matchSearch =
      search === "" ||
      p.job_title.toLowerCase().includes(search.toLowerCase()) ||
      p.department.toLowerCase().includes(search.toLowerCase()) ||
      p.recruiter_name.toLowerCase().includes(search.toLowerCase());
    return matchSLA && matchSearch;
  });

  const counts = {
    em_atraso: processes.filter((p) => p.sla_status === "em_atraso").length,
    em_risco: processes.filter((p) => p.sla_status === "em_risco").length,
    no_prazo: processes.filter((p) => p.sla_status === "no_prazo").length,
  };

  const sectionsToShow =
    slaFilter === "todos"
      ? SLA_SECTIONS.filter((s) => filtered.some((p) => p.sla_status === s.key))
      : SLA_SECTIONS.filter((s) => s.key === slaFilter);

  return (
    <div className="flex flex-col min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur px-6 py-4">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-base font-semibold text-primary">
              Painel de Processos Seletivos
            </h1>
            <p className="text-xs text-muted mt-0.5">
              {loading ? "Carregando..." : `${processes.length} processos · clique para consultar o agente`}
            </p>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* SLA summary pills */}
            {!loading && (
              <div className="flex gap-1.5">
                {Object.entries(counts).map(([k, v]) => (
                  <button
                    key={k}
                    onClick={() => setSlaFilter(k === slaFilter ? "todos" : (k as SLAFilter))}
                    className={`transition-opacity ${k !== slaFilter && slaFilter !== "todos" ? "opacity-40" : ""}`}
                  >
                    <SLABadge status={k as SLAStatus} />
                    <span className="ml-1 text-xs text-muted">{v}</span>
                  </button>
                ))}
              </div>
            )}

            <a
              href="/"
              className="rounded-lg border border-border px-3 py-1.5 text-xs text-muted hover:text-primary hover:bg-accent transition-colors"
            >
              ← Voltar ao chat
            </a>
          </div>
        </div>

        {/* Search */}
        <div className="mt-3">
          <input
            type="text"
            placeholder="Buscar por vaga, departamento ou recrutador..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-border bg-background-secondary px-3 py-2 text-sm text-primary placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-border"
          />
        </div>
      </header>

      <main className="flex-1 p-6">
        {loading && (
          <div className="flex items-center justify-center h-40">
            <div className="flex items-center gap-2 text-muted text-sm">
              <span className="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full" />
              Carregando processos...
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-400">
            {error}
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div className="flex items-center justify-center h-40 text-muted text-sm">
            Nenhum processo encontrado com os filtros selecionados.
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-8">
            {sectionsToShow.map((section) => {
              const items = filtered.filter((p) => p.sla_status === section.key);
              if (items.length === 0) return null;
              return (
                <section key={section.key}>
                  <div className={`inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 mb-4 ${section.color}`}>
                    <span className="text-xs font-semibold uppercase tracking-wide">
                      {section.label}
                    </span>
                    <span className="text-xs opacity-70">{items.length}</span>
                  </div>
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {items.map((process) => (
                      <ProcessCard
                        key={process.process_id}
                        process={process}
                        onAction={handleAction}
                      />
                    ))}
                  </div>
                </section>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
