import pytest

from schemas.job_opening import CreateJobOpeningInput, CreateJobOpeningOutput
from tools.job_opening_server import create_job_opening
from utils.exceptions import RecruitmentServiceError


async def test_create_job_opening_success(mocker):
    mocker.patch(
        "services.job_opening.create_job_opening_service",
        return_value=CreateJobOpeningOutput(
            opening_id="OPEN-ABC123",
            job_posting_id="JOB-DEF456",
            job_description_draft="Rascunho da JD",
            status="success",
            message="Abertura criada com sucesso.",
        ),
    )

    result = await create_job_opening(
        CreateJobOpeningInput(
            position_title="Engenheiro de Software",
            department="Tecnologia",
            seniority_level="Pleno",
            deadline_days=30,
            requestor_name="Ana Lima",
        )
    )

    assert result.status == "success"
    assert result.opening_id == "OPEN-ABC123"
    assert result.job_posting_id == "JOB-DEF456"


async def test_create_job_opening_invalid_input():
    with pytest.raises(Exception):
        CreateJobOpeningInput(
            position_title=123,
            department=None,
            seniority_level="Pleno",
            deadline_days=30,
            requestor_name="Ana Lima",
        )


async def test_create_job_opening_service_failure(mocker):
    mocker.patch(
        "services.job_opening.create_job_opening_service",
        side_effect=RecruitmentServiceError("Falha simulada"),
    )

    with pytest.raises(RecruitmentServiceError):
        await create_job_opening(
            CreateJobOpeningInput(
                position_title="Dev Backend",
                department="Tech",
                seniority_level="Sênior",
                deadline_days=45,
                requestor_name="Carlos Mendes",
            )
        )
