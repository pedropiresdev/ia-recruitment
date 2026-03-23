from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.job_opening import JobOpeningModel
from utils.exceptions import JobOpeningNotFoundError


async def create_job_opening(session: AsyncSession, model: JobOpeningModel) -> JobOpeningModel:
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def get_job_opening_by_id(session: AsyncSession, opening_id: str) -> JobOpeningModel:
    result = await session.execute(select(JobOpeningModel).where(JobOpeningModel.id == opening_id))
    opening = result.scalar_one_or_none()
    if not opening:
        raise JobOpeningNotFoundError(f"Abertura {opening_id} não encontrada.")
    return opening


async def update_job_description(session: AsyncSession, opening_id: str, job_description: str) -> JobOpeningModel:
    opening = await get_job_opening_by_id(session, opening_id)
    opening.job_description_draft = job_description
    await session.commit()
    await session.refresh(opening)
    return opening


async def link_to_posting(session: AsyncSession, opening_id: str, job_posting_id: str) -> JobOpeningModel:
    opening = await get_job_opening_by_id(session, opening_id)
    opening.job_posting_id = job_posting_id
    await session.commit()
    await session.refresh(opening)
    return opening


async def mark_approved(session: AsyncSession, opening_id: str) -> JobOpeningModel:
    opening = await get_job_opening_by_id(session, opening_id)
    opening.approved = True
    await session.commit()
    await session.refresh(opening)
    return opening
