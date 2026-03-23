import pytest

from schemas.process import (
    GetProcessDetailInput,
    GetProcessDetailOutput,
    ListProcessesInput,
    ListProcessesOutput,
    ProcessStatus,
    QuickAction,
    SLAStatus,
    SuspendProcessInput,
    SuspendProcessOutput,
)
from tools.process_management_server import (
    get_process_detail,
    list_processes,
    suspend_process,
)
from utils.exceptions import RecruitmentServiceError, SuspensionReasonRequiredError


async def test_list_processes_success(mocker):
    mocker.patch(
        "services.process_management.list_processes_service",
        return_value=ListProcessesOutput(
            processes=[],
            total=0,
            message="Nenhum processo encontrado.",
        ),
    )

    result = await list_processes(ListProcessesInput())
    assert result.total == 0


async def test_get_process_detail_success(mocker):
    mocker.patch(
        "services.process_management.get_process_detail_service",
        return_value=GetProcessDetailOutput(
            process_id="PROC-001",
            job_title="Head de Produto",
            department="Produto",
            recruiter_name="Mariana Silva",
            status=ProcessStatus.IN_PROGRESS,
            sla_status=SLAStatus.OVERDUE,
            sla_deadline_date="2024-01-15",
            days_since_last_update=10,
            open_candidates_count=5,
            bottleneck_description="Candidatos aguardando feedback da entrevista técnica.",
            days_overdue=5,
            recommended_actions=[
                QuickAction(
                    label="Rascunhar mensagem para o gestor",
                    prompt="Rascunhe mensagem para o gestor do processo PROC-001.",
                )
            ],
            message="Detalhes do processo recuperados.",
        ),
    )

    result = await get_process_detail(GetProcessDetailInput(process_id="PROC-001"))
    assert result.process_id == "PROC-001"
    assert result.sla_status == SLAStatus.OVERDUE
    assert result.days_overdue == 5


async def test_suspend_process_with_reason(mocker):
    mocker.patch(
        "services.process_management.suspend_process_service",
        return_value=SuspendProcessOutput(
            process_id="PROC-001",
            status=ProcessStatus.SUSPENDED,
            suspension_reason="Congelamento de headcount aprovado pela diretoria.",
            message="Processo suspenso com sucesso.",
        ),
    )

    result = await suspend_process(
        SuspendProcessInput(
            process_id="PROC-001",
            suspension_reason="Congelamento de headcount aprovado pela diretoria.",
        )
    )
    assert result.status == ProcessStatus.SUSPENDED


async def test_suspend_process_missing_reason():
    with pytest.raises(Exception):
        SuspendProcessInput(process_id="PROC-001", suspension_reason="")


async def test_suspend_process_service_failure(mocker):
    mocker.patch(
        "services.process_management.suspend_process_service",
        side_effect=RecruitmentServiceError("Falha simulada"),
    )

    with pytest.raises(RecruitmentServiceError):
        await suspend_process(
            SuspendProcessInput(
                process_id="PROC-001",
                suspension_reason="Motivo válido de teste.",
            )
        )
