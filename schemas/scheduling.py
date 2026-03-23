from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScheduleInterviewInput(BaseModel):
    model_config = ConfigDict(strict=True)

    candidate_id: str = Field(description="ID do candidato a ser entrevistado")
    process_id: str = Field(description="ID do processo seletivo")
    interviewer_id: str = Field(description="ID do entrevistador responsável")
    proposed_datetime: str = Field(
        description="Data e hora proposta no formato ISO 8601: YYYY-MM-DDTHH:MM"
    )
    interview_type: str = Field(
        description="Tipo de entrevista: 'tecnica', 'cultural', 'gestao', 'rh'"
    )
    duration_minutes: int = Field(
        default=60, description="Duração da entrevista em minutos"
    )
    notes: Optional[str] = Field(
        default=None, description="Observações para o agendamento"
    )


class ScheduleInterviewOutput(BaseModel):
    interview_id: str = Field(description="ID único do agendamento criado")
    candidate_id: str = Field(description="ID do candidato")
    process_id: str = Field(description="ID do processo seletivo")
    scheduled_datetime: str = Field(
        description="Data e hora confirmada do agendamento"
    )
    interviewer_id: str = Field(description="ID do entrevistador")
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado do agendamento")


class RescheduleInterviewInput(BaseModel):
    model_config = ConfigDict(strict=True)

    interview_id: str = Field(description="ID do agendamento a ser remarcado")
    new_datetime: str = Field(
        description="Nova data e hora no formato ISO 8601: YYYY-MM-DDTHH:MM"
    )
    reason: str = Field(description="Motivo da remarcação")


class RescheduleInterviewOutput(BaseModel):
    interview_id: str = Field(description="ID do agendamento remarcado")
    previous_datetime: str = Field(description="Data e hora anterior")
    new_datetime: str = Field(description="Nova data e hora confirmada")
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado da remarcação")


class GetAvailableSlotsInput(BaseModel):
    model_config = ConfigDict(strict=True)

    interviewer_id: str = Field(
        description="ID do entrevistador para verificar disponibilidade"
    )
    date_from: str = Field(
        description="Data inicial da busca no formato YYYY-MM-DD"
    )
    date_to: str = Field(
        description="Data final da busca no formato YYYY-MM-DD"
    )
    duration_minutes: int = Field(
        default=60, description="Duração necessária da entrevista em minutos"
    )


class TimeSlot(BaseModel):
    start_datetime: str = Field(description="Início do horário disponível")
    end_datetime: str = Field(description="Fim do horário disponível")


class GetAvailableSlotsOutput(BaseModel):
    interviewer_id: str = Field(description="ID do entrevistador")
    available_slots: list[TimeSlot] = Field(
        description="Lista de horários disponíveis"
    )
    message: str = Field(description="Mensagem legível com os horários disponíveis")


class CancelInterviewInput(BaseModel):
    model_config = ConfigDict(strict=True)

    interview_id: str = Field(description="ID do agendamento a ser cancelado")
    reason: str = Field(description="Motivo do cancelamento")


class CancelInterviewOutput(BaseModel):
    interview_id: str = Field(description="ID do agendamento cancelado")
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado do cancelamento")


class GetInterviewsByProcessInput(BaseModel):
    process_id: str = Field(description="ID do processo seletivo")


class InterviewDetail(BaseModel):
    interview_id: str = Field(description="ID único da entrevista")
    candidate_id: str = Field(description="ID do candidato")
    candidate_name: str = Field(description="Nome completo do candidato")
    process_id: str = Field(description="ID do processo seletivo")
    interviewer_id: str = Field(description="ID do entrevistador")
    interview_type: str = Field(description="Tipo de entrevista")
    scheduled_datetime: str = Field(description="Data e hora da entrevista (ISO 8601)")
    duration_minutes: int = Field(description="Duração em minutos")
    status: str = Field(description="Status: agendada, cancelada ou realizada")
    notes: Optional[str] = Field(default=None, description="Observações do agendamento")
    cancellation_reason: Optional[str] = Field(default=None, description="Motivo do cancelamento")
    reschedule_reason: Optional[str] = Field(default=None, description="Motivo da remarcação")


class GetInterviewsByProcessOutput(BaseModel):
    process_id: str = Field(description="ID do processo seletivo")
    interviews: list[InterviewDetail] = Field(description="Lista de entrevistas do processo")
    total: int = Field(description="Total de entrevistas")
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class GetInterviewInput(BaseModel):
    interview_id: str = Field(description="ID único da entrevista")


class GetInterviewOutput(BaseModel):
    interview: InterviewDetail = Field(description="Dados completos da entrevista")
    message: str = Field(description="Mensagem legível com o resultado da consulta")


class InterviewerInfo(BaseModel):
    interviewer_id: str = Field(description="ID único do entrevistador")
    name: str = Field(description="Nome completo do entrevistador")
    role: str = Field(description="Cargo do entrevistador")
    department: str = Field(description="Departamento do entrevistador")


class InterviewTypeInfo(BaseModel):
    interview_type: str = Field(description="Código do tipo de entrevista")
    label: str = Field(description="Nome legível do tipo de entrevista")
    description: str = Field(description="Descrição do objetivo da entrevista")


class GetSchedulingOptionsOutput(BaseModel):
    interviewers: list[InterviewerInfo] = Field(description="Lista de entrevistadores disponíveis")
    interview_types: list[InterviewTypeInfo] = Field(description="Tipos de entrevista disponíveis")
    message: str = Field(description="Mensagem de contexto")
