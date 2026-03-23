export type ProcessStatus = "em_aberto" | "em_andamento" | "suspenso" | "encerrado";
export type SLAStatus = "no_prazo" | "em_risco" | "em_atraso";

export type RecruitmentProcess = {
  process_id: string;
  job_title: string;
  department: string;
  recruiter_name: string;
  status: ProcessStatus;
  sla_status: SLAStatus;
  sla_deadline_date: string;
  days_since_last_update: number;
  open_candidates_count: number;
};

export type QuickAction = {
  label: string;
  prompt: string;
};

export type ProcessTimelineEvent = {
  stage: string;
  date: string;
  actor: string;
  notes?: string;
};

export type Candidate = {
  id: string;
  full_name: string;
  position_applied: string;
  current_stage: string;
  days_in_stage: number;
};

export type CandidatesByStage = {
  stage_name: string;
  candidates: Candidate[];
};

export type ProcessDetail = RecruitmentProcess & {
  bottleneck_description: string;
  days_overdue: number;
  recommended_actions: QuickAction[];
  timeline: ProcessTimelineEvent[];
  candidates_by_stage: CandidatesByStage[];
};
