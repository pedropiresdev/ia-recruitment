from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CreateJobOpeningInput(BaseModel):
    model_config = ConfigDict(strict=True)

    position_title: str = Field(description="Título da posição a ser aberta")
    department: str = Field(description="Departamento solicitante da contratação")
    seniority_level: str = Field(
        description="Nível de senioridade: Júnior, Pleno, Sênior, Especialista, Gestão"
    )
    deadline_days: int = Field(description="Prazo em dias para preenchimento da vaga")
    requirements: Optional[str] = Field(
        default=None,
        description="Requisitos técnicos e comportamentais da posição",
    )
    salary_range: Optional[str] = Field(
        default=None,
        description="Faixa salarial esperada, ex: 'R$8.000 - R$12.000'",
    )
    requestor_name: str = Field(
        description="Nome do gestor que está solicitando a abertura"
    )


class CreateJobOpeningOutput(BaseModel):
    opening_id: str = Field(description="ID único da abertura de posição")
    job_posting_id: str = Field(
        description="ID da vaga criada no ATS, vinculada à abertura"
    )
    job_description_draft: str = Field(
        description="Rascunho da Job Description gerado automaticamente"
    )
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado da operação")


class CollectOpeningDetailsInput(BaseModel):
    model_config = ConfigDict(strict=True)

    opening_id: str = Field(description="ID da abertura de posição em andamento")
    missing_fields: list[str] = Field(
        description="Lista de campos que precisam ser coletados via conversa"
    )


class CollectOpeningDetailsOutput(BaseModel):
    opening_id: str = Field(description="ID da abertura de posição")
    collected_fields: dict = Field(description="Campos coletados e seus valores")
    remaining_fields: list[str] = Field(
        description="Campos que ainda precisam ser coletados"
    )
    is_complete: bool = Field(
        description="Indica se todos os campos obrigatórios foram coletados"
    )
    message: str = Field(description="Mensagem legível com o resultado da coleta")


class GenerateJobDescriptionInput(BaseModel):
    model_config = ConfigDict(strict=True)

    opening_id: str = Field(
        description="ID da abertura de posição para gerar a Job Description"
    )


class GenerateJobDescriptionOutput(BaseModel):
    opening_id: str = Field(description="ID da abertura de posição")
    job_description: str = Field(
        description="Rascunho completo da Job Description gerado"
    )
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado da operação")


class LinkOpeningToPostingInput(BaseModel):
    model_config = ConfigDict(strict=True)

    opening_id: str = Field(description="ID da abertura de posição")
    job_posting_id: str = Field(description="ID da vaga no ATS a ser vinculada")


class LinkOpeningToPostingOutput(BaseModel):
    opening_id: str = Field(description="ID da abertura de posição")
    job_posting_id: str = Field(description="ID da vaga no ATS vinculada")
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado do vínculo")


class SendApprovalReminderInput(BaseModel):
    model_config = ConfigDict(strict=True)

    opening_id: str = Field(description="ID da abertura de posição sem aprovação")
    requestor_name: str = Field(description="Nome do gestor para envio do lembrete")


class SendApprovalReminderOutput(BaseModel):
    opening_id: str = Field(description="ID da abertura de posição")
    reminder_sent: bool = Field(description="Indica se o lembrete foi enviado")
    status: str = Field(description="Status da operação: 'success' ou 'error'")
    message: str = Field(description="Mensagem legível com o resultado do envio")
