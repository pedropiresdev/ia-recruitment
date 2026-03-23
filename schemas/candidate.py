from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CandidateStage(str, Enum):
    APPLIED = "inscrito"
    SCREENING = "triagem"
    INTERVIEW = "entrevista"
    TECHNICAL = "tecnico"
    OFFER = "proposta"
    HIRED = "contratado"
    REJECTED = "reprovado"
    WITHDRAWN = "desistiu"


class ScreenCandidateInput(BaseModel):
    model_config = ConfigDict(strict=True)

    candidate_id: str = Field(description="ID único do candidato")
    process_id: str = Field(description="ID do processo seletivo")
    resume_text: Optional[str] = Field(
        default=None, description="Texto do currículo do candidato"
    )
    notes: Optional[str] = Field(
        default=None, description="Anotações do recrutador sobre o candidato"
    )


class ScreenCandidateOutput(BaseModel):
    candidate_id: str = Field(description="ID do candidato avaliado")
    process_id: str = Field(description="ID do processo seletivo")
    recommendation: str = Field(
        description="Recomendação: 'aprovar', 'reprovar' ou 'pendente'"
    )
    justification: str = Field(
        description="Justificativa da recomendação em linguagem natural"
    )
    score: Optional[float] = Field(
        default=None, description="Pontuação de aderência ao perfil (0 a 10)"
    )
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado da triagem")


class MoveCandidateStageInput(BaseModel):
    candidate_id: str = Field(description="ID do candidato a ser movido")
    process_id: str = Field(description="ID do processo seletivo")
    target_stage: CandidateStage = Field(description="Etapa de destino do candidato")
    reason: Optional[str] = Field(
        default=None, description="Motivo da movimentação de etapa"
    )


class MoveCandidateStageOutput(BaseModel):
    candidate_id: str = Field(description="ID do candidato")
    process_id: str = Field(description="ID do processo seletivo")
    previous_stage: str = Field(description="Etapa anterior do candidato")
    current_stage: str = Field(description="Nova etapa do candidato")
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado da movimentação")


class GetCandidateProfileInput(BaseModel):
    model_config = ConfigDict(strict=True)

    candidate_id: str = Field(description="ID único do candidato")


class CandidateProfile(BaseModel):
    candidate_id: str = Field(description="ID único do candidato")
    full_name: str = Field(description="Nome completo do candidato")
    email: str = Field(description="E-mail do candidato")
    phone: Optional[str] = Field(default=None, description="Telefone do candidato")
    current_stage: CandidateStage = Field(description="Etapa atual do candidato")
    process_id: str = Field(description="ID do processo seletivo")
    days_in_stage: int = Field(
        description="Número de dias que o candidato está na etapa atual"
    )
    applied_at: str = Field(description="Data de inscrição no formato YYYY-MM-DD")


class GetCandidateProfileOutput(BaseModel):
    profile: CandidateProfile = Field(description="Perfil completo do candidato")
    message: str = Field(description="Mensagem legível com o resultado da consulta")
