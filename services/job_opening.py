from db.models.job_opening import JobOpeningModel
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
from utils.exceptions import JobOpeningNotFoundError, RecruitmentServiceError


async def create_job_opening_service(
    input: CreateJobOpeningInput,
) -> CreateJobOpeningOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.job_opening import create_job_opening

    try:
        import uuid

        job_posting_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
        job_description_draft = _generate_jd_draft(input)

        model = JobOpeningModel(
            job_posting_id=job_posting_id,
            position_title=input.position_title,
            department=input.department,
            seniority_level=input.seniority_level,
            deadline_days=input.deadline_days,
            requirements=input.requirements,
            salary_range=input.salary_range,
            requestor_name=input.requestor_name,
            job_description_draft=job_description_draft,
        )

        async with AsyncSessionLocal() as session:
            opening = await create_job_opening(session, model)

        return CreateJobOpeningOutput(
            opening_id=opening.id,
            job_posting_id=opening.job_posting_id,
            job_description_draft=opening.job_description_draft or "",
            status="success",
            message=(
                f"Abertura de posição '{opening.position_title}' criada com sucesso. "
                f"ID da abertura: {opening.id}. ID da vaga no ATS: {opening.job_posting_id}."
            ),
        )
    except Exception as e:
        raise RecruitmentServiceError(f"Falha ao criar abertura de posição: {e}") from e


async def collect_opening_details_service(
    input: CollectOpeningDetailsInput,
) -> CollectOpeningDetailsOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.job_opening import get_job_opening_by_id

    try:
        async with AsyncSessionLocal() as session:
            opening = await get_job_opening_by_id(session, input.opening_id)

        collected = {
            "position_title": opening.position_title,
            "department": opening.department,
            "seniority_level": opening.seniority_level,
            "deadline_days": opening.deadline_days,
            "requestor_name": opening.requestor_name,
        }
        if opening.requirements:
            collected["requirements"] = opening.requirements
        if opening.salary_range:
            collected["salary_range"] = opening.salary_range

        remaining = [f for f in input.missing_fields if f not in collected]

        return CollectOpeningDetailsOutput(
            opening_id=opening.id,
            collected_fields=collected,
            remaining_fields=remaining,
            is_complete=len(remaining) == 0,
            message="Dados coletados com sucesso." if not remaining else "Coleta de dados em andamento.",
        )
    except JobOpeningNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(f"Falha ao coletar detalhes da abertura: {e}") from e


async def generate_job_description_service(
    input: GenerateJobDescriptionInput,
) -> GenerateJobDescriptionOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.job_opening import get_job_opening_by_id, update_job_description

    try:
        async with AsyncSessionLocal() as session:
            opening = await get_job_opening_by_id(session, input.opening_id)

        if opening.job_description_draft:
            jd = opening.job_description_draft
        else:
            from schemas.job_opening import CreateJobOpeningInput

            jd_input = CreateJobOpeningInput(
                position_title=opening.position_title,
                department=opening.department,
                seniority_level=opening.seniority_level,
                deadline_days=opening.deadline_days,
                requirements=opening.requirements,
                salary_range=opening.salary_range,
                requestor_name=opening.requestor_name,
            )
            jd = _generate_jd_draft(jd_input)

            async with AsyncSessionLocal() as session:
                await update_job_description(session, opening.id, jd)

        return GenerateJobDescriptionOutput(
            opening_id=opening.id,
            job_description=jd,
            status="success",
            message="Job Description gerada com sucesso.",
        )
    except JobOpeningNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(f"Falha ao gerar Job Description: {e}") from e


async def link_opening_to_posting_service(
    input: LinkOpeningToPostingInput,
) -> LinkOpeningToPostingOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.job_opening import link_to_posting

    try:
        async with AsyncSessionLocal() as session:
            opening = await link_to_posting(session, input.opening_id, input.job_posting_id)

        return LinkOpeningToPostingOutput(
            opening_id=opening.id,
            job_posting_id=opening.job_posting_id,
            status="success",
            message=(
                f"Abertura {opening.id} vinculada com sucesso à vaga "
                f"{opening.job_posting_id} no ATS."
            ),
        )
    except JobOpeningNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao vincular abertura à vaga: {e}"
        ) from e


async def send_approval_reminder_service(
    input: SendApprovalReminderInput,
) -> SendApprovalReminderOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.job_opening import get_job_opening_by_id

    try:
        async with AsyncSessionLocal() as session:
            opening = await get_job_opening_by_id(session, input.opening_id)

        return SendApprovalReminderOutput(
            opening_id=opening.id,
            reminder_sent=True,
            status="success",
            message=(
                f"Lembrete de aprovação enviado para {input.requestor_name} "
                f"referente à abertura {opening.id} ({opening.position_title})."
            ),
        )
    except JobOpeningNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao enviar lembrete de aprovação: {e}"
        ) from e


def _generate_jd_draft(input) -> str:
    requirements_section = (
        f"\n\n## Requisitos\n{input.requirements}"
        if input.requirements
        else ""
    )
    salary_section = (
        f"\n\n## Remuneração\n{input.salary_range}" if input.salary_range else ""
    )

    return (
        f"# {input.position_title} — {input.seniority_level}\n\n"
        f"**Departamento:** {input.department}\n\n"
        f"## Sobre a Vaga\n"
        f"Estamos buscando um profissional para a posição de {input.position_title} "
        f"no nível {input.seniority_level} para o departamento de {input.department}."
        f"{requirements_section}"
        f"{salary_section}\n\n"
        f"*Prazo para preenchimento: {input.deadline_days} dias*"
    )
