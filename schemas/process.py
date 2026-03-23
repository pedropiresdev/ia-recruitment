from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProcessStatus(str, Enum):
    OPEN = "em_aberto"
    IN_PROGRESS = "em_andamento"
    SUSPENDED = "suspenso"
    CLOSED = "encerrado"


class SLAStatus(str, Enum):
    ON_TIME = "no_prazo"
    AT_RISK = "em_risco"
    OVERDUE = "em_atraso"


class ProcessSummary(BaseModel):
    process_id: str = Field(description="ID único do processo seletivo")
    job_title: str = Field(description="Título da vaga")
    department: str = Field(description="Departamento responsável")
    recruiter_name: str = Field(description="Nome do recrutador responsável")
    status: ProcessStatus = Field(description="Status atual do processo")
    sla_status: SLAStatus = Field(description="Status do SLA do processo")
    sla_deadline_date: str = Field(description="Data limite do SLA no formato YYYY-MM-DD")
    days_since_last_update: int = Field(
        description="Número de dias desde a última atualização do processo"
    )
    open_candidates_count: int = Field(
        description="Número de candidatos ativos no processo"
    )


class TimelineEvent(BaseModel):
    stage: str = Field(description="Nome da etapa")
    date: str = Field(description="Data do evento no formato YYYY-MM-DD")
    actor: str = Field(description="Responsável pela ação")
    notes: Optional[str] = Field(default=None, description="Observações sobre o evento")


class CandidateSummary(BaseModel):
    candidate_id: str = Field(description="ID único do candidato")
    full_name: str = Field(description="Nome completo do candidato")
    current_stage: str = Field(description="Etapa atual do candidato no processo")
    days_in_stage: int = Field(
        description="Número de dias que o candidato está na etapa atual"
    )


class CandidatesByStage(BaseModel):
    stage_name: str = Field(description="Nome da etapa do processo seletivo")
    candidates: list[CandidateSummary] = Field(
        description="Lista de candidatos nesta etapa"
    )


class QuickAction(BaseModel):
    label: str = Field(description="Rótulo do botão de ação rápida")
    prompt: str = Field(
        description="Prompt enviado ao agente ao clicar na ação rápida"
    )


class ListProcessesInput(BaseModel):
    status_filter: Optional[ProcessStatus] = Field(
        default=None, description="Filtrar por status do processo"
    )
    sla_filter: Optional[SLAStatus] = Field(
        default=None, description="Filtrar por status de SLA"
    )
    recruiter_id: Optional[str] = Field(
        default=None, description="Filtrar por recrutador responsável"
    )


class ListProcessesOutput(BaseModel):
    processes: list[ProcessSummary] = Field(
        description="Lista de processos seletivos filtrados"
    )
    total: int = Field(description="Total de processos retornados")
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class GetSLAStatusInput(BaseModel):
    model_config = ConfigDict(strict=True)

    process_id: Optional[str] = Field(
        default=None,
        description="ID do processo para verificar SLA. Se vazio, retorna todos",
    )


class GetSLAStatusOutput(BaseModel):
    process_id: Optional[str] = Field(
        default=None, description="ID do processo consultado"
    )
    sla_status: SLAStatus = Field(description="Status do SLA")
    days_until_deadline: int = Field(
        description="Dias restantes até o vencimento do SLA (negativo se atrasado)"
    )
    message: str = Field(description="Mensagem legível com o status do SLA")


class GetProcessDetailInput(BaseModel):
    model_config = ConfigDict(strict=True)

    process_id: str = Field(description="ID único do processo seletivo")


class GetProcessDetailOutput(BaseModel):
    process_id: str = Field(description="ID único do processo seletivo")
    job_title: str = Field(description="Título da vaga")
    department: str = Field(description="Departamento responsável")
    recruiter_name: str = Field(description="Nome do recrutador responsável")
    status: ProcessStatus = Field(description="Status atual do processo")
    sla_status: SLAStatus = Field(description="Status do SLA")
    sla_deadline_date: str = Field(description="Data limite do SLA")
    days_since_last_update: int = Field(
        description="Dias desde a última atualização"
    )
    open_candidates_count: int = Field(description="Número de candidatos ativos")
    bottleneck_description: str = Field(
        description="Descrição do gargalo atual identificado no processo"
    )
    days_overdue: int = Field(
        description="Dias de atraso no SLA (0 se não está atrasado)"
    )
    recommended_actions: list[QuickAction] = Field(
        description="Lista de ações rápidas recomendadas com prompts"
    )
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class GetProcessTimelineOutput(BaseModel):
    process_id: str = Field(description="ID do processo seletivo")
    timeline: list[TimelineEvent] = Field(
        description="Histórico cronológico de etapas e datas"
    )
    bottleneck_stage: Optional[str] = Field(
        default=None,
        description="Etapa identificada como gargalo no processo",
    )
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class GetCandidatesByStageOutput(BaseModel):
    process_id: str = Field(description="ID do processo seletivo")
    stages: list[CandidatesByStage] = Field(
        description="Candidatos agrupados por etapa"
    )
    total_candidates: int = Field(description="Total de candidatos no processo")
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class GetProcessSummaryOutput(BaseModel):
    process_id: str = Field(description="ID do processo seletivo")
    summary: str = Field(
        description="Resumo executivo do processo em texto estruturado"
    )
    sla_status: SLAStatus = Field(description="Status do SLA")
    recommended_actions: list[QuickAction] = Field(
        description="Ações recomendadas para o processo"
    )
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class SuspendProcessInput(BaseModel):
    model_config = ConfigDict(strict=True)

    process_id: str = Field(
        description="ID único do processo seletivo a ser suspenso"
    )
    suspension_reason: str = Field(
        description="Motivo obrigatório da suspensão do processo — nunca pode ser vazio"
    )


class SuspendProcessOutput(BaseModel):
    process_id: str = Field(description="ID do processo suspenso")
    status: ProcessStatus = Field(description="Novo status do processo")
    suspension_reason: str = Field(description="Motivo registrado da suspensão")
    message: str = Field(description="Mensagem legível com o resultado da operação")


class GetOverdueSLAInput(BaseModel):
    model_config = ConfigDict(strict=True)

    days_ahead: int = Field(
        default=2,
        description="Número de dias à frente para incluir processos com SLA a vencer",
    )


class GetOverdueSLAOutput(BaseModel):
    overdue_processes: list[ProcessSummary] = Field(
        description="Processos com SLA vencido"
    )
    at_risk_processes: list[ProcessSummary] = Field(
        description="Processos com SLA a vencer nos próximos dias"
    )
    total_critical: int = Field(
        description="Total de processos críticos (vencidos + em risco)"
    )
    message: str = Field(description="Mensagem legível com o resultado da consulta")
