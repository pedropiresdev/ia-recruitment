from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.candidate import CandidateModel
from utils.exceptions import CandidateNotFoundError


async def create_candidate(session: AsyncSession, model: CandidateModel) -> CandidateModel:
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def get_candidate_by_id(session: AsyncSession, candidate_id: str) -> CandidateModel:
    result = await session.execute(
        select(CandidateModel).where(CandidateModel.id == candidate_id)
    )
    candidate = result.scalar_one_or_none()
    if not candidate:
        raise CandidateNotFoundError(f"Candidato {candidate_id} não encontrado.")
    return candidate


async def list_candidates_by_process(
    session: AsyncSession, process_id: str
) -> list[CandidateModel]:
    result = await session.execute(
        select(CandidateModel)
        .where(CandidateModel.process_id == process_id)
        .order_by(CandidateModel.current_stage, CandidateModel.applied_at)
    )
    return list(result.scalars().all())


async def move_stage(
    session: AsyncSession,
    candidate_id: str,
    target_stage: str,
) -> CandidateModel:
    candidate = await get_candidate_by_id(session, candidate_id)
    candidate.current_stage = target_stage
    candidate.days_in_stage = 0
    candidate.stage_updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(candidate)
    return candidate


async def update_screening(
    session: AsyncSession,
    candidate_id: str,
    recommendation: str,
    notes: str | None = None,
) -> CandidateModel:
    candidate = await get_candidate_by_id(session, candidate_id)
    candidate.screening_recommendation = recommendation
    candidate.screening_notes = notes
    await session.commit()
    await session.refresh(candidate)
    return candidate
