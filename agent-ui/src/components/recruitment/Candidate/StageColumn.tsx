import type { CandidatesByStage } from "@/types/recruitment";
import { CandidateCard } from "./CandidateCard";

type StageColumnProps = {
  stage: CandidatesByStage;
};

export function StageColumn({ stage }: StageColumnProps) {
  return (
    <div className="flex-1 min-w-48 rounded-xl border border-border bg-background-secondary p-3">
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-semibold text-primary">{stage.stage_name}</h4>
        <span className="rounded-full bg-accent px-2 py-0.5 text-xs text-muted">
          {stage.candidates.length}
        </span>
      </div>
      <div className="space-y-2">
        {stage.candidates.length === 0 ? (
          <p className="text-xs text-muted py-4 text-center">Nenhum candidato</p>
        ) : (
          stage.candidates.map((candidate) => (
            <CandidateCard key={candidate.id} candidate={candidate} />
          ))
        )}
      </div>
    </div>
  );
}
