"use client";

import { useState } from "react";
import type { ProcessStatus, RecruitmentProcess, SLAStatus } from "@/types/recruitment";
import { ProcessRow } from "./ProcessRow";

type FilterStatus = ProcessStatus | "todos";
type FilterSLA = SLAStatus | "todos";

type ProcessTableProps = {
  processes: RecruitmentProcess[];
  onRowClick: (prompt: string) => void;
};

export function ProcessTable({ processes, onRowClick }: ProcessTableProps) {
  const [statusFilter, setStatusFilter] = useState<FilterStatus>("todos");
  const [slaFilter, setSlaFilter] = useState<FilterSLA>("todos");

  const filtered = processes.filter((p) => {
    const matchStatus = statusFilter === "todos" || p.status === statusFilter;
    const matchSLA = slaFilter === "todos" || p.sla_status === slaFilter;
    return matchStatus && matchSLA;
  });

  return (
    <div className="rounded-xl border border-border bg-background-secondary overflow-hidden">
      <div className="flex items-center gap-3 px-4 py-3 border-b border-border">
        <span className="text-sm font-medium text-primary">Filtrar:</span>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as FilterStatus)}
          className="rounded-lg border border-border bg-background px-2 py-1 text-sm text-primary"
        >
          <option value="todos">Todos os status</option>
          <option value="em_aberto">Em aberto</option>
          <option value="em_andamento">Em andamento</option>
          <option value="suspenso">Suspenso</option>
          <option value="encerrado">Encerrado</option>
        </select>
        <select
          value={slaFilter}
          onChange={(e) => setSlaFilter(e.target.value as FilterSLA)}
          className="rounded-lg border border-border bg-background px-2 py-1 text-sm text-primary"
        >
          <option value="todos">Todos os SLAs</option>
          <option value="no_prazo">No prazo</option>
          <option value="em_risco">Em risco</option>
          <option value="em_atraso">Em atraso</option>
        </select>
        <span className="ml-auto text-xs text-muted">
          {filtered.length} processo{filtered.length !== 1 ? "s" : ""}
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-xs text-muted uppercase tracking-wide">
              <th className="px-4 py-2 text-left font-medium">Vaga</th>
              <th className="px-4 py-2 text-left font-medium">Departamento</th>
              <th className="px-4 py-2 text-left font-medium">Recrutador</th>
              <th className="px-4 py-2 text-left font-medium">Status</th>
              <th className="px-4 py-2 text-left font-medium">SLA</th>
              <th className="px-4 py-2 text-left font-medium">Candidatos</th>
              <th className="px-4 py-2 text-left font-medium">Última atualização</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-muted">
                  Nenhum processo encontrado com os filtros selecionados.
                </td>
              </tr>
            ) : (
              filtered.map((process) => (
                <ProcessRow
                  key={process.process_id}
                  process={process}
                  onRowClick={onRowClick}
                />
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
