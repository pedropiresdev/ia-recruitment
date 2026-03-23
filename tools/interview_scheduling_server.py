from fastmcp import FastMCP

from schemas.scheduling import (
    CancelInterviewInput,
    CancelInterviewOutput,
    GetAvailableSlotsInput,
    GetAvailableSlotsOutput,
    GetInterviewInput,
    GetInterviewOutput,
    GetInterviewsByProcessInput,
    GetInterviewsByProcessOutput,
    GetSchedulingOptionsOutput,
    RescheduleInterviewInput,
    RescheduleInterviewOutput,
    ScheduleInterviewInput,
    ScheduleInterviewOutput,
)
from services.interview_scheduling import (
    cancel_interview_service,
    get_available_slots_service,
    get_interview_service,
    get_interviews_by_process_service,
    get_scheduling_options_service,
    reschedule_interview_service,
    schedule_interview_service,
)

mcp = FastMCP(name="interview-scheduling-server")


@mcp.tool()
async def schedule_interview(input: ScheduleInterviewInput) -> ScheduleInterviewOutput:
    """
    Agenda uma entrevista para um candidato em um processo seletivo.
    Use quando o recrutador quiser marcar uma entrevista técnica, cultural, com gestão ou RH.
    Verificar disponibilidade do entrevistador antes de confirmar o agendamento.
    """
    return await schedule_interview_service(input)


@mcp.tool()
async def reschedule_interview(
    input: RescheduleInterviewInput,
) -> RescheduleInterviewOutput:
    """
    Remarca uma entrevista para uma nova data e hora.
    Use quando o recrutador ou candidato precisar alterar o horário de uma entrevista já
    agendada. O motivo da remarcação é obrigatório para registro no histórico.
    """
    return await reschedule_interview_service(input)


@mcp.tool()
async def get_available_slots(
    input: GetAvailableSlotsInput,
) -> GetAvailableSlotsOutput:
    """
    Retorna os horários disponíveis de um entrevistador em um período específico.
    Use antes de agendar ou remarcar uma entrevista para apresentar opções ao recrutador.
    Sempre consultar a disponibilidade antes de propor um horário ao candidato.
    """
    return await get_available_slots_service(input)


@mcp.tool()
async def get_interviews_by_process(
    input: GetInterviewsByProcessInput,
) -> GetInterviewsByProcessOutput:
    """
    Lista todas as entrevistas agendadas de um processo seletivo.
    Use para dar uma visão geral das entrevistas do processo, incluindo status,
    tipo, candidatos e horários. Enriquecida com o nome do candidato.
    """
    return await get_interviews_by_process_service(input)


@mcp.tool()
async def get_interview(input: GetInterviewInput) -> GetInterviewOutput:
    """
    Retorna os dados completos de uma entrevista específica pelo ID.
    Use para consultar detalhes de um agendamento: candidato, entrevistador,
    horário, tipo, status e observações.
    """
    return await get_interview_service(input)


@mcp.tool()
async def get_scheduling_options() -> GetSchedulingOptionsOutput:
    """
    Retorna a lista de entrevistadores disponíveis e os tipos de entrevista suportados.
    Use SEMPRE antes de agendar uma entrevista para apresentar as opções ao recrutador,
    permitindo que ele escolha o entrevistador (e seu ID) e o tipo de entrevista correto.
    """
    return await get_scheduling_options_service()


@mcp.tool()
async def cancel_interview(input: CancelInterviewInput) -> CancelInterviewOutput:
    """
    Cancela uma entrevista agendada. O motivo do cancelamento é obrigatório.
    Use quando o candidato desistir, o processo for suspenso ou o entrevistador não
    estiver disponível. Sempre confirmar com o recrutador antes de cancelar.
    """
    return await cancel_interview_service(input)
