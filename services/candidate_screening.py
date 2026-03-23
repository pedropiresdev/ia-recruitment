from schemas.candidate import (
    CandidateProfile,
    CandidateStage,
    GetCandidateProfileInput,
    GetCandidateProfileOutput,
    MoveCandidateStageInput,
    MoveCandidateStageOutput,
    ScreenCandidateInput,
    ScreenCandidateOutput,
)
from utils.exceptions import CandidateNotFoundError, RecruitmentServiceError


async def screen_candidate_service(
    input: ScreenCandidateInput,
) -> ScreenCandidateOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.candidate import get_candidate_by_id, update_screening

    try:
        async with AsyncSessionLocal() as session:
            candidate = await get_candidate_by_id(session, input.candidate_id)

        recommendation = candidate.screening_recommendation or "pendente"
        justification = candidate.screening_notes or (
            "Candidato encontrado no sistema. Avalie o currículo para definir a recomendação."
        )

        if input.notes:
            async with AsyncSessionLocal() as session:
                candidate = await update_screening(
                    session, input.candidate_id, recommendation, input.notes
                )
            justification = input.notes

        return ScreenCandidateOutput(
            candidate_id=candidate.id,
            process_id=candidate.process_id,
            recommendation=recommendation,
            justification=justification,
            score=None,
            status="success",
            message=f"Triagem do candidato {candidate.full_name} ({candidate.id}) concluída.",
        )
    except CandidateNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao realizar triagem do candidato {input.candidate_id}: {e}"
        ) from e


async def move_candidate_stage_service(
    input: MoveCandidateStageInput,
) -> MoveCandidateStageOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.candidate import get_candidate_by_id, move_stage

    try:
        async with AsyncSessionLocal() as session:
            candidate = await get_candidate_by_id(session, input.candidate_id)
            previous_stage = candidate.current_stage

        async with AsyncSessionLocal() as session:
            candidate = await move_stage(session, input.candidate_id, input.target_stage.value)

        return MoveCandidateStageOutput(
            candidate_id=candidate.id,
            process_id=candidate.process_id,
            previous_stage=previous_stage,
            current_stage=candidate.current_stage,
            status="success",
            message=(
                f"Candidato {candidate.full_name} movido de '{previous_stage}' para "
                f"'{candidate.current_stage}' com sucesso."
            ),
        )
    except CandidateNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao mover candidato {input.candidate_id}: {e}"
        ) from e


async def get_candidate_profile_service(
    input: GetCandidateProfileInput,
) -> GetCandidateProfileOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.candidate import get_candidate_by_id

    try:
        async with AsyncSessionLocal() as session:
            c = await get_candidate_by_id(session, input.candidate_id)

        profile = CandidateProfile(
            candidate_id=c.id,
            full_name=c.full_name,
            email=c.email,
            phone=c.phone,
            current_stage=CandidateStage(c.current_stage),
            process_id=c.process_id,
            days_in_stage=c.days_in_stage,
            applied_at=c.applied_at.strftime("%Y-%m-%d"),
        )

        return GetCandidateProfileOutput(
            profile=profile,
            message=f"Perfil do candidato {c.full_name} recuperado com sucesso.",
        )
    except CandidateNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar perfil do candidato {input.candidate_id}: {e}"
        ) from e
