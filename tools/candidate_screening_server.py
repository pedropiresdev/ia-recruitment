from fastmcp import FastMCP

from schemas.candidate import (
    GetCandidateProfileInput,
    GetCandidateProfileOutput,
    MoveCandidateStageInput,
    MoveCandidateStageOutput,
    ScreenCandidateInput,
    ScreenCandidateOutput,
)
from services.candidate_screening import (
    get_candidate_profile_service,
    move_candidate_stage_service,
    screen_candidate_service,
)

mcp = FastMCP(name="candidate-screening-server")


@mcp.tool()
async def screen_candidate(input: ScreenCandidateInput) -> ScreenCandidateOutput:
    """
    Realiza a triagem de um candidato com base no currículo e nos critérios da vaga.
    Use para avaliar se o candidato está apto para avançar no processo seletivo.
    Retorna recomendação (aprovar/reprovar/pendente) e justificativa detalhada.
    """
    return await screen_candidate_service(input)


@mcp.tool()
async def move_candidate_stage(
    input: MoveCandidateStageInput,
) -> MoveCandidateStageOutput:
    """
    Move um candidato para uma nova etapa do processo seletivo.
    Use para avançar ou retroceder candidatos no funil de seleção.
    Sempre confirmar com o recrutador antes de mover para etapas irreversíveis como
    'contratado' ou 'reprovado'.
    """
    return await move_candidate_stage_service(input)


@mcp.tool()
async def get_candidate_profile(
    input: GetCandidateProfileInput,
) -> GetCandidateProfileOutput:
    """
    Retorna o perfil completo de um candidato, incluindo etapa atual e dados de contato.
    Use para obter informações detalhadas sobre um candidato específico antes de tomar
    decisões de movimentação ou agendamento.
    """
    return await get_candidate_profile_service(input)
