import type { CandidatesByStage } from '@/types/recruitment'
import { CandidateCard } from './CandidateCard'

type StageColumnProps = {
  stage: CandidatesByStage
}

export function StageColumn({ stage }: StageColumnProps) {
  return (
    <div className="min-w-48 flex-1 rounded-xl border border-border bg-background-secondary p-3">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-primary">
          {stage.stage_name}
        </h4>
        <span className="rounded-full bg-accent px-2 py-0.5 text-xs text-muted">
          {stage.candidates.length}
        </span>
      </div>
      <div className="space-y-2">
        {stage.candidates.length === 0 ? (
          <p className="py-4 text-center text-xs text-muted">
            Nenhum candidato
          </p>
        ) : (
          stage.candidates.map((candidate) => (
            <CandidateCard key={candidate.id} candidate={candidate} />
          ))
        )}
      </div>
    </div>
  )
}
