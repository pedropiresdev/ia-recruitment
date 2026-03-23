from fastmcp import FastMCP

from schemas.job_opening import (
    CollectOpeningDetailsInput,
    CollectOpeningDetailsOutput,
    CreateJobOpeningInput,
    CreateJobOpeningOutput,
    GenerateJobDescriptionInput,
    GenerateJobDescriptionOutput,
    LinkOpeningToPostingInput,
    LinkOpeningToPostingOutput,
    SendApprovalReminderInput,
    SendApprovalReminderOutput,
)
from services.job_opening import (
    collect_opening_details_service,
    create_job_opening_service,
    generate_job_description_service,
    link_opening_to_posting_service,
    send_approval_reminder_service,
)

mcp = FastMCP(name="job-opening-server")


@mcp.tool()
async def create_job_opening(input: CreateJobOpeningInput) -> CreateJobOpeningOutput:
    """
    Inicia o fluxo unificado de abertura de posição e criação de vaga.
    Use quando o agente detectar uma solicitação de contratação.
    Coleta dados da posição, gera a Job Description e vincula a vaga no ATS com um ID único.
    Nunca chamar com seniority_level ou deadline_days vazios — coletar antes via conversa.
    """
    return await create_job_opening_service(input)


@mcp.tool()
async def collect_opening_details(
    input: CollectOpeningDetailsInput,
) -> CollectOpeningDetailsOutput:
    """
    Coleta os dados faltantes de uma abertura de posição em andamento via conversa natural.
    Use quando create_job_opening não puder ser chamado por falta de campos obrigatórios
    como seniority_level ou deadline_days. Retorna quais campos já foram coletados e
    quais ainda faltam.
    """
    return await collect_opening_details_service(input)


@mcp.tool()
async def generate_job_description(
    input: GenerateJobDescriptionInput,
) -> GenerateJobDescriptionOutput:
    """
    Gera o rascunho da Job Description a partir dos dados coletados da abertura de posição.
    Use após coletar todos os campos obrigatórios da abertura.
    O rascunho deve ser apresentado ao recrutador para revisão antes da publicação.
    """
    return await generate_job_description_service(input)


@mcp.tool()
async def link_opening_to_posting(
    input: LinkOpeningToPostingInput,
) -> LinkOpeningToPostingOutput:
    """
    Vincula a abertura de posição à vaga no ATS com um ID único compartilhado.
    Use para garantir a rastreabilidade entre a solicitação de contratação e a vaga publicada.
    Sempre chamar após a criação da vaga no ATS para manter o vínculo entre os registros.
    """
    return await link_opening_to_posting_service(input)


@mcp.tool()
async def send_approval_reminder(
    input: SendApprovalReminderInput,
) -> SendApprovalReminderOutput:
    """
    Envia um lembrete ao gestor quando a abertura de posição não for aprovada dentro do prazo.
    Use automaticamente quando o prazo em deadline_days for atingido sem aprovação do gestor.
    """
    return await send_approval_reminder_service(input)
