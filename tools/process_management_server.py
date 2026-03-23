from fastmcp import FastMCP

from schemas.process import (
    GetCandidatesByStageOutput,
    GetOverdueSLAInput,
    GetOverdueSLAOutput,
    GetProcessDetailInput,
    GetProcessDetailOutput,
    GetProcessSummaryOutput,
    GetProcessTimelineOutput,
    GetSLAStatusInput,
    GetSLAStatusOutput,
    ListProcessesInput,
    ListProcessesOutput,
    SuspendProcessInput,
    SuspendProcessOutput,
)
from services.process_management import (
    get_candidates_by_stage_service,
    get_overdue_sla_service,
    get_process_detail_service,
    get_process_summary_service,
    get_process_timeline_service,
    get_sla_status_service,
    list_processes_service,
    suspend_process_service,
)

mcp = FastMCP(name="process-management-server")


@mcp.tool()
async def list_processes(input: ListProcessesInput) -> ListProcessesOutput:
    """
    Lista os processos seletivos com filtros por status: em aberto, em andamento, suspenso,
    com SLA em atraso. Use para responder perguntas como 'quais vagas estão abertas?' ou
    'quantos processos estão em andamento?'
    """
    return await list_processes_service(input)


@mcp.tool()
async def get_sla_status(input: GetSLAStatusInput) -> GetSLAStatusOutput:
    """
    Verifica o status de SLA de um processo seletivo específico ou de todos os processos.
    Use para identificar quais processos estão em risco ou em atraso.
    Retorna dias restantes até o vencimento (negativo se já vencido).
    """
    return await get_sla_status_service(input)


@mcp.tool()
async def get_process_summary(input: GetProcessDetailInput) -> GetProcessSummaryOutput:
    """
    Retorna um resumo executivo de um processo seletivo com ações recomendadas.
    Use para respostas rápidas quando o recrutador precisar de uma visão geral sem os
    detalhes completos de candidatos e timeline.
    """
    return await get_process_summary_service(input)


@mcp.tool()
async def get_process_detail(input: GetProcessDetailInput) -> GetProcessDetailOutput:
    """
    Retorna detalhes completos de um processo seletivo: candidatos por etapa, histórico,
    SLA e próximas ações. Use quando o recrutador perguntar sobre um processo específico,
    como 'me dê um resumo da vaga Head de Produto'. Sempre chamar em conjunto com
    get_process_timeline e get_candidates_by_stage para compor a resposta completa.
    """
    return await get_process_detail_service(input)


@mcp.tool()
async def get_process_timeline(
    input: GetProcessDetailInput,
) -> GetProcessTimelineOutput:
    """
    Retorna o histórico cronológico de etapas e datas de um processo seletivo.
    Use para identificar gargalos, calcular tempo entre etapas e detectar onde o processo
    parou. Sempre chamar em conjunto com get_process_detail ao detalhar um processo
    com SLA em atraso.
    """
    return await get_process_timeline_service(input)


@mcp.tool()
async def get_candidates_by_stage(
    input: GetProcessDetailInput,
) -> GetCandidatesByStageOutput:
    """
    Retorna os candidatos agrupados por etapa de um processo seletivo.
    Use para responder 'quais candidatos estão aguardando retorno?' ou para montar a visão
    do funil de seleção. Sempre chamar em conjunto com get_process_detail ao detalhar
    um processo completo.
    """
    return await get_candidates_by_stage_service(input)


@mcp.tool()
async def suspend_process(input: SuspendProcessInput) -> SuspendProcessOutput:
    """
    Suspende um processo seletivo. O motivo da suspensão é obrigatório.
    Se o recrutador não informar o motivo, solicitar antes de chamar esta tool.
    O motivo é registrado no histórico do processo para consultas futuras.
    Nunca chamar com suspension_reason vazio, nulo ou genérico como 'motivo não informado'.
    """
    return await suspend_process_service(input)


@mcp.tool()
async def get_overdue_sla_processes(
    input: GetOverdueSLAInput,
) -> GetOverdueSLAOutput:
    """
    Lista os processos seletivos com SLA vencido ou a vencer nos próximos N dias.
    Use para monitoramento proativo de SLA e para sugerir ações corretivas ao recrutador.
    O parâmetro days_ahead define quantos dias à frente considerar como 'em risco'.
    """
    return await get_overdue_sla_service(input)
