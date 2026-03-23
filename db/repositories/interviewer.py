from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.interviewer import InterviewerModel
from utils.exceptions import RecruitmentServiceError


async def list_interviewers(session: AsyncSession) -> list[InterviewerModel]:
    result = await session.execute(
        select(InterviewerModel).order_by(InterviewerModel.name)
    )
    return list(result.scalars().all())


async def get_interviewer_by_id(session: AsyncSession, interviewer_id: str) -> InterviewerModel:
    result = await session.execute(
        select(InterviewerModel).where(InterviewerModel.id == interviewer_id)
    )
    interviewer = result.scalar_one_or_none()
    if not interviewer:
        raise RecruitmentServiceError(f"Entrevistador {interviewer_id} não encontrado.")
    return interviewer
