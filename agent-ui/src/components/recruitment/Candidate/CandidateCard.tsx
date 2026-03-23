import type { Candidate } from "@/types/recruitment";

type CandidateCardProps = {
  candidate: Candidate;
};

export function CandidateCard({ candidate }: CandidateCardProps) {
  return (
    <div className="rounded-lg border border-border bg-background p-3 space-y-1">
      <p className="text-sm font-medium text-primary">{candidate.full_name}</p>
      <p className="text-xs text-muted">{candidate.position_applied}</p>
      <p className="text-xs text-muted">
        {candidate.days_in_stage}d na etapa atual
      </p>
    </div>
  );
}
