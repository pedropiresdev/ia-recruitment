import type { SLAStatus } from "@/types/recruitment";

const SLA_STYLES: Record<SLAStatus, string> = {
  no_prazo: "bg-green-500/15 text-green-400 border border-green-500/30",
  em_risco: "bg-yellow-500/15 text-yellow-400 border border-yellow-500/30",
  em_atraso: "bg-red-500/15 text-red-400 border border-red-500/30",
};

const SLA_LABELS: Record<SLAStatus, string> = {
  no_prazo: "No prazo",
  em_risco: "Em risco",
  em_atraso: "Em atraso",
};

type SLABadgeProps = { status: SLAStatus };

export function SLABadge({ status }: SLABadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${SLA_STYLES[status]}`}
    >
      {SLA_LABELS[status]}
    </span>
  );
}
