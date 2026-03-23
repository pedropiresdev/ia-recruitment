from datetime import datetime, timezone

from schemas.process import (
    CandidatesByStage,
    CandidateSummary,
    GetCandidatesByStageOutput,
    GetOverdueSLAInput,
    GetOverdueSLAOutput,
    GetProcessDetailInput,
    GetProcessDetailOutput,
    GetProcessSummaryOutput,
    GetProcessTimelineOutput,
    GetSLAStatusInput,
    GetSLAStatusOutput,
    ListProcessesInput,
    ListProcessesOutput,
    ProcessStatus,
    ProcessSummary,
    QuickAction,
    SLAStatus,
    SuspendProcessInput,
    SuspendProcessOutput,
    TimelineEvent,
)
from utils.exceptions import (
    ProcessNotFoundError,
    RecruitmentServiceError,
    SuspensionReasonRequiredError,
)


def _days_since(dt: datetime) -> int:
    return (datetime.now(timezone.utc) - dt).days


def _days_until(dt: datetime | None) -> int:
    if not dt:
        return 0
    return (dt - datetime.now(timezone.utc)).days


def _quick_actions(process_id: str, job_title: str) -> list[QuickAction]:
    return [
        QuickAction(
            label="Rascunhar mensagem para o gestor",
            prompt=f'Rascunhe uma mensagem de cobrança para o gestor responsável pelo processo "{job_title}" (ID: {process_id}).',
        ),
        QuickAction(
            label="Reagendar etapa",
            prompt=f'Quero reagendar a próxima etapa do processo "{job_title}" (ID: {process_id}).',
        ),
        QuickAction(
            label="Ver candidatos em espera",
            prompt=f'Quais candidatos estão aguardando retorno no processo "{job_title}" (ID: {process_id})?',
        ),
    ]


def _bottleneck(process, timeline_events) -> str:
    if process.status == "suspenso":
        return f"Processo suspenso. Motivo: {process.suspension_reason}"
    if timeline_events:
        last = sorted(timeline_events, key=lambda e: e.event_date)[-1]
        days = _days_since(last.event_date)
        return f"Última movimentação na etapa '{last.stage}' há {days} dias. {last.notes or ''}".strip()
    return "Nenhuma movimentação registrada no processo."


async def list_processes_service(input: ListProcessesInput) -> ListProcessesOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import list_processes

    try:
        async with AsyncSessionLocal() as session:
            rows = await list_processes(
                session,
                status_filter=input.status_filter.value if input.status_filter else None,
                sla_filter=input.sla_filter.value if input.sla_filter else None,
                recruiter_id=input.recruiter_id,
            )

        processes = [
            ProcessSummary(
                process_id=p.id,
                job_title=p.job_title,
                department=p.department,
                recruiter_name=p.recruiter_name,
                status=ProcessStatus(p.status),
                sla_status=SLAStatus(p.sla_status),
                sla_deadline_date=p.sla_deadline_date.strftime("%Y-%m-%d") if p.sla_deadline_date else "",
                days_since_last_update=_days_since(p.updated_at),
                open_candidates_count=p.open_candidates_count,
            )
            for p in rows
        ]

        total = len(processes)
        msg = (
            f"{total} processo(s) encontrado(s)."
            if total
            else "Nenhum processo encontrado com os filtros informados."
        )
        return ListProcessesOutput(processes=processes, total=total, message=msg)

    except Exception as e:
        raise RecruitmentServiceError(f"Falha ao listar processos: {e}") from e


async def get_sla_status_service(input: GetSLAStatusInput) -> GetSLAStatusOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import get_process_by_id

    try:
        async with AsyncSessionLocal() as session:
            p = await get_process_by_id(session, input.process_id)

        days = _days_until(p.sla_deadline_date)
        overdue = days < 0
        msg = (
            f"SLA vencido há {abs(days)} dia(s)."
            if overdue
            else f"SLA dentro do prazo — {days} dia(s) restantes."
        )
        return GetSLAStatusOutput(
            process_id=p.id,
            sla_status=SLAStatus(p.sla_status),
            days_until_deadline=days,
            message=msg,
        )

    except ProcessNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(f"Falha ao verificar SLA: {e}") from e


async def get_process_summary_service(
    input: GetProcessDetailInput,
) -> GetProcessSummaryOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import get_process_by_id

    try:
        async with AsyncSessionLocal() as session:
            p = await get_process_by_id(session, input.process_id)

        days_overdue = abs(_days_until(p.sla_deadline_date)) if p.sla_status == "em_atraso" else 0
        summary = (
            f"**{p.job_title}** — {p.department}\n"
            f"- Recrutador: {p.recruiter_name}\n"
            f"- Status: {p.status} | SLA: {p.sla_status}\n"
            f"- Candidatos ativos: {p.open_candidates_count}\n"
            f"- Última atualização: {_days_since(p.updated_at)} dia(s) atrás\n"
            + (f"- **Atraso: {days_overdue} dia(s)**\n" if days_overdue else "")
        )
        return GetProcessSummaryOutput(
            process_id=p.id,
            summary=summary,
            sla_status=SLAStatus(p.sla_status),
            recommended_actions=_quick_actions(p.id, p.job_title),
            message="Resumo gerado com sucesso.",
        )

    except ProcessNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao gerar resumo do processo {input.process_id}: {e}"
        ) from e


async def get_process_detail_service(
    input: GetProcessDetailInput,
) -> GetProcessDetailOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import get_process_by_id

    try:
        async with AsyncSessionLocal() as session:
            p = await get_process_by_id(session, input.process_id)

        days_overdue = abs(_days_until(p.sla_deadline_date)) if p.sla_status == "em_atraso" else 0
        bottleneck = _bottleneck(p, p.timeline)

        return GetProcessDetailOutput(
            process_id=p.id,
            job_title=p.job_title,
            department=p.department,
            recruiter_name=p.recruiter_name,
            status=ProcessStatus(p.status),
            sla_status=SLAStatus(p.sla_status),
            sla_deadline_date=p.sla_deadline_date.strftime("%Y-%m-%d") if p.sla_deadline_date else "",
            days_since_last_update=_days_since(p.updated_at),
            open_candidates_count=p.open_candidates_count,
            bottleneck_description=bottleneck,
            days_overdue=days_overdue,
            recommended_actions=_quick_actions(p.id, p.job_title),
            message=f"Detalhes do processo {p.id} recuperados com sucesso.",
        )

    except ProcessNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar detalhes do processo {input.process_id}: {e}"
        ) from e


async def get_process_timeline_service(
    input: GetProcessDetailInput,
) -> GetProcessTimelineOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import get_process_by_id

    try:
        async with AsyncSessionLocal() as session:
            p = await get_process_by_id(session, input.process_id)

        events = sorted(p.timeline, key=lambda e: e.event_date)
        timeline = [
            TimelineEvent(
                stage=e.stage,
                date=e.event_date.strftime("%Y-%m-%d"),
                actor=e.actor,
                notes=e.notes,
            )
            for e in events
        ]

        bottleneck_stage = events[-1].stage if events else None

        return GetProcessTimelineOutput(
            process_id=p.id,
            timeline=timeline,
            bottleneck_stage=bottleneck_stage,
            message=f"{len(timeline)} evento(s) encontrado(s) na timeline.",
        )

    except ProcessNotFoundError:
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar timeline do processo {input.process_id}: {e}"
        ) from e


async def get_candidates_by_stage_service(
    input: GetProcessDetailInput,
) -> GetCandidatesByStageOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.candidate import list_candidates_by_process

    try:
        async with AsyncSessionLocal() as session:
            candidates = await list_candidates_by_process(session, input.process_id)

        stages: dict[str, list[CandidateSummary]] = {}
        for c in candidates:
            stages.setdefault(c.current_stage, []).append(
                CandidateSummary(
                    candidate_id=c.id,
                    full_name=c.full_name,
                    current_stage=c.current_stage,
                    days_in_stage=c.days_in_stage,
                )
            )

        stage_list = [
            CandidatesByStage(stage_name=stage, candidates=cands)
            for stage, cands in stages.items()
        ]

        return GetCandidatesByStageOutput(
            process_id=input.process_id,
            stages=stage_list,
            total_candidates=len(candidates),
            message=f"{len(candidates)} candidato(s) encontrado(s).",
        )

    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar candidatos do processo {input.process_id}: {e}"
        ) from e


async def suspend_process_service(
    input: SuspendProcessInput,
) -> SuspendProcessOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import add_timeline_event, suspend_process

    if not input.suspension_reason or not input.suspension_reason.strip():
        raise SuspensionReasonRequiredError(
            "O motivo da suspensão é obrigatório e não pode ser vazio."
        )

    try:
        async with AsyncSessionLocal() as session:
            p = await suspend_process(session, input.process_id, input.suspension_reason)
            await add_timeline_event(
                session,
                process_id=input.process_id,
                stage="Suspensão",
                actor="Sistema",
                notes=f"Motivo: {input.suspension_reason}",
            )

        return SuspendProcessOutput(
            process_id=p.id,
            status=ProcessStatus(p.status),
            suspension_reason=p.suspension_reason,
            message=f"Processo {p.id} suspenso. Motivo registrado: {p.suspension_reason}",
        )

    except (SuspensionReasonRequiredError, ProcessNotFoundError):
        raise
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao suspender processo {input.process_id}: {e}"
        ) from e


async def get_overdue_sla_service(
    input: GetOverdueSLAInput,
) -> GetOverdueSLAOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.process import get_overdue_processes

    try:
        async with AsyncSessionLocal() as session:
            overdue_rows, at_risk_rows = await get_overdue_processes(session, input.days_ahead)

        def to_summary(p) -> ProcessSummary:
            return ProcessSummary(
                process_id=p.id,
                job_title=p.job_title,
                department=p.department,
                recruiter_name=p.recruiter_name,
                status=ProcessStatus(p.status),
                sla_status=SLAStatus(p.sla_status),
                sla_deadline_date=p.sla_deadline_date.strftime("%Y-%m-%d") if p.sla_deadline_date else "",
                days_since_last_update=_days_since(p.updated_at),
                open_candidates_count=p.open_candidates_count,
            )

        overdue = [to_summary(p) for p in overdue_rows]
        at_risk = [to_summary(p) for p in at_risk_rows]
        total = len(overdue) + len(at_risk)

        msg = (
            f"{len(overdue)} processo(s) com SLA vencido e {len(at_risk)} em risco."
            if total
            else f"Nenhum processo crítico nos próximos {input.days_ahead} dias."
        )

        return GetOverdueSLAOutput(
            overdue_processes=overdue,
            at_risk_processes=at_risk,
            total_critical=total,
            message=msg,
        )

    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar processos com SLA crítico: {e}"
        ) from e
