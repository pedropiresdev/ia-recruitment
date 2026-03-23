import pytest

from schemas.job_opening import CreateJobOpeningInput
from services.job_opening import create_job_opening_service


async def test_create_job_opening_generates_ids():
    result = await create_job_opening_service(
        CreateJobOpeningInput(
            position_title="Engenheiro de Dados",
            department="Dados",
            seniority_level="Sênior",
            deadline_days=30,
            requestor_name="Pedro Neves",
        )
    )

    assert result.status == "success"
    assert result.opening_id.startswith("OPEN-")
    assert result.job_posting_id.startswith("JOB-")
    assert len(result.job_description_draft) > 0


async def test_create_job_opening_ids_are_unique():
    input_data = CreateJobOpeningInput(
        position_title="Analista de RH",
        department="Recursos Humanos",
        seniority_level="Pleno",
        deadline_days=20,
        requestor_name="Fernanda Costa",
    )

    result1 = await create_job_opening_service(input_data)
    result2 = await create_job_opening_service(input_data)

    assert result1.opening_id != result2.opening_id
    assert result1.job_posting_id != result2.job_posting_id


async def test_job_description_contains_position_info():
    result = await create_job_opening_service(
        CreateJobOpeningInput(
            position_title="Product Manager",
            department="Produto",
            seniority_level="Especialista",
            deadline_days=45,
            requestor_name="Lucas Rocha",
            requirements="Experiência com roadmap e OKRs",
            salary_range="R$15.000 - R$20.000",
        )
    )

    assert "Product Manager" in result.job_description_draft
    assert "Especialista" in result.job_description_draft
    assert "Produto" in result.job_description_draft
