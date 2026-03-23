import pytest

from schemas.process import (
    GetProcessDetailInput,
    ListProcessesInput,
    ProcessStatus,
    SuspendProcessInput,
)
from services.process_management import (
    list_processes_service,
    suspend_process_service,
)
from utils.exceptions import SuspensionReasonRequiredError


async def test_list_processes_returns_output():
    result = await list_processes_service(ListProcessesInput())
    assert result.total == 0
    assert isinstance(result.processes, list)


async def test_suspend_process_with_valid_reason():
    result = await suspend_process_service(
        SuspendProcessInput(
            process_id="PROC-001",
            suspension_reason="Congelamento de headcount aprovado pela diretoria.",
        )
    )
    assert result.status == ProcessStatus.SUSPENDED
    assert result.suspension_reason != ""


async def test_suspend_process_empty_reason_raises():
    with pytest.raises(SuspensionReasonRequiredError):
        await suspend_process_service(
            SuspendProcessInput(
                process_id="PROC-001",
                suspension_reason="   ",
            )
        )


async def test_get_process_detail_returns_recommended_actions():
    from services.process_management import get_process_detail_service

    result = await get_process_detail_service(
        GetProcessDetailInput(process_id="PROC-999")
    )
    assert len(result.recommended_actions) >= 3
    labels = [a.label for a in result.recommended_actions]
    assert "Rascunhar mensagem para o gestor" in labels
    assert "Reagendar etapa" in labels
    assert "Ver candidatos em espera" in labels
