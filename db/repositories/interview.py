from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.interview import InterviewModel
from utils.exceptions import RecruitmentServiceError


async def create_interview(session: AsyncSession, model: InterviewModel) -> InterviewModel:
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def get_interview_by_id(session: AsyncSession, interview_id: str) -> InterviewModel:
    result = await session.execute(
        select(InterviewModel).where(InterviewModel.id == interview_id)
    )
    interview = result.scalar_one_or_none()
    if not interview:
        raise RecruitmentServiceError(f"Entrevista {interview_id} não encontrada.")
    return interview


async def list_interviews_by_process(
    session: AsyncSession, process_id: str
) -> list[InterviewModel]:
    result = await session.execute(
        select(InterviewModel)
        .where(InterviewModel.process_id == process_id)
        .order_by(InterviewModel.scheduled_datetime)
    )
    return list(result.scalars().all())


async def get_interviewer_slots(
    session: AsyncSession,
    interviewer_id: str,
    date_from: datetime,
    date_to: datetime,
) -> list[InterviewModel]:
    """Retorna entrevistas agendadas do entrevistador no período para calcular disponibilidade."""
    result = await session.execute(
        select(InterviewModel).where(
            and_(
                InterviewModel.interviewer_id == interviewer_id,
                InterviewModel.scheduled_datetime >= date_from,
                InterviewModel.scheduled_datetime <= date_to,
                InterviewModel.status == "agendada",
            )
        ).order_by(InterviewModel.scheduled_datetime)
    )
    return list(result.scalars().all())


async def reschedule_interview(
    session: AsyncSession,
    interview_id: str,
    new_datetime: datetime,
    reason: str,
) -> InterviewModel:
    interview = await get_interview_by_id(session, interview_id)
    interview.scheduled_datetime = new_datetime
    interview.reschedule_reason = reason
    interview.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(interview)
    return interview


async def cancel_interview(
    session: AsyncSession,
    interview_id: str,
    reason: str,
) -> InterviewModel:
    interview = await get_interview_by_id(session, interview_id)
    interview.status = "cancelada"
    interview.cancellation_reason = reason
    interview.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(interview)
    return interview
