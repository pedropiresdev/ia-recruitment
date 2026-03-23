from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.process import ProcessTimelineModel, SelectionProcessModel
from utils.exceptions import ProcessNotFoundError, SuspensionReasonRequiredError


async def create_process(session: AsyncSession, model: SelectionProcessModel) -> SelectionProcessModel:
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def get_process_by_id(session: AsyncSession, process_id: str) -> SelectionProcessModel:
    result = await session.execute(
        select(SelectionProcessModel)
        .where(SelectionProcessModel.id == process_id)
        .options(selectinload(SelectionProcessModel.timeline))
    )
    process = result.scalar_one_or_none()
    if not process:
        raise ProcessNotFoundError(f"Processo {process_id} não encontrado.")
    return process


async def list_processes(
    session: AsyncSession,
    status_filter: str | None = None,
    sla_filter: str | None = None,
    recruiter_id: str | None = None,
) -> list[SelectionProcessModel]:
    query = select(SelectionProcessModel)
    if status_filter:
        query = query.where(SelectionProcessModel.status == status_filter)
    if sla_filter:
        query = query.where(SelectionProcessModel.sla_status == sla_filter)
    if recruiter_id:
        query = query.where(SelectionProcessModel.recruiter_id == recruiter_id)
    query = query.order_by(SelectionProcessModel.updated_at.desc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def suspend_process(
    session: AsyncSession,
    process_id: str,
    suspension_reason: str,
) -> SelectionProcessModel:
    if not suspension_reason or not suspension_reason.strip():
        raise SuspensionReasonRequiredError(
            "O motivo da suspensão é obrigatório e não pode ser vazio."
        )
    process = await get_process_by_id(session, process_id)
    process.status = "suspenso"
    process.sla_status = "no_prazo"
    process.suspension_reason = suspension_reason
    process.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(process)
    return process


async def update_sla_status(
    session: AsyncSession,
    process_id: str,
    sla_status: str,
) -> SelectionProcessModel:
    process = await get_process_by_id(session, process_id)
    process.sla_status = sla_status
    process.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(process)
    return process


async def add_timeline_event(
    session: AsyncSession,
    process_id: str,
    stage: str,
    actor: str,
    event_date: datetime | None = None,
    notes: str | None = None,
) -> ProcessTimelineModel:
    event = ProcessTimelineModel(
        process_id=process_id,
        stage=stage,
        actor=actor,
        event_date=event_date or datetime.now(timezone.utc),
        notes=notes,
    )
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def get_overdue_processes(
    session: AsyncSession,
    days_ahead: int = 2,
) -> tuple[list[SelectionProcessModel], list[SelectionProcessModel]]:
    from datetime import timedelta

    now = datetime.now(timezone.utc)
    threshold = now + timedelta(days=days_ahead)

    overdue_result = await session.execute(
        select(SelectionProcessModel).where(
            SelectionProcessModel.sla_status == "em_atraso",
            SelectionProcessModel.status.notin_(["suspenso", "encerrado"]),
        )
    )
    at_risk_result = await session.execute(
        select(SelectionProcessModel).where(
            SelectionProcessModel.sla_status == "em_risco",
            SelectionProcessModel.status.notin_(["suspenso", "encerrado"]),
            SelectionProcessModel.sla_deadline_date <= threshold,
        )
    )
    return list(overdue_result.scalars().all()), list(at_risk_result.scalars().all())
