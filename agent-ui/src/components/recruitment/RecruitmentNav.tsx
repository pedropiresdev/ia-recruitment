"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export function RecruitmentNav() {
  const [criticalCount, setCriticalCount] = useState<number | null>(null);

  useEffect(() => {
    fetch("/api/processes?sla_filter=em_atraso")
      .then((r) => r.json())
      .then((data) => setCriticalCount(data.total ?? 0))
      .catch(() => {});
  }, []);

  return (
    <div className="absolute top-3 right-3 z-10">
      <Link
        href="/processos"
        className="relative flex items-center gap-2 rounded-lg border border-border bg-background-secondary px-3 py-1.5 text-xs text-muted hover:text-primary hover:bg-accent transition-colors"
      >
        <svg
          className="w-3.5 h-3.5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
        </svg>
        <span>Painel de Processos</span>
        {criticalCount !== null && criticalCount > 0 && (
          <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-red-500 text-white text-[10px] font-bold">
            {criticalCount}
          </span>
        )}
      </Link>
    </div>
  );
}
