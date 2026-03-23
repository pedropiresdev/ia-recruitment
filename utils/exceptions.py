class RecruitmentServiceError(Exception):
    """Base exception para todos os erros do serviço de recrutamento."""


class CandidateNotFoundError(RecruitmentServiceError):
    """Levantada quando o registro de um candidato não é encontrado."""


class ProcessNotFoundError(RecruitmentServiceError):
    """Levantada quando o processo seletivo não é encontrado."""


class SuspensionReasonRequiredError(RecruitmentServiceError):
    """Levantada quando uma suspensão é tentada sem motivo registrado."""


class InterviewSlotUnavailableError(RecruitmentServiceError):
    """Levantada quando o horário de entrevista solicitado não está disponível."""


class ATSIntegrationError(RecruitmentServiceError):
    """Levantada quando a integração com o ATS falha."""


class SLACalculationError(RecruitmentServiceError):
    """Levantada quando não é possível calcular o SLA de um processo."""


class JobOpeningNotFoundError(RecruitmentServiceError):
    """Levantada quando a abertura de posição não é encontrada."""
