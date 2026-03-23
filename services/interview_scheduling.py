from datetime import datetime, timedelta, timezone

from db.models.interview import InterviewModel
from schemas.scheduling import (
    CancelInterviewInput,
    CancelInterviewOutput,
    GetAvailableSlotsInput,
    GetAvailableSlotsOutput,
    GetInterviewInput,
    GetInterviewOutput,
    GetInterviewsByProcessInput,
    GetInterviewsByProcessOutput,
    GetSchedulingOptionsOutput,
    InterviewDetail,
    InterviewerInfo,
    InterviewTypeInfo,
    RescheduleInterviewInput,
    RescheduleInterviewOutput,
    ScheduleInterviewInput,
    ScheduleInterviewOutput,
    TimeSlot,
)

from utils.exceptions import RecruitmentServiceError


def _to_interview_detail(interview: InterviewModel, candidate_name: str) -> InterviewDetail:
    return InterviewDetail(
        interview_id=interview.id,
        candidate_id=interview.candidate_id,
        candidate_name=candidate_name,
        process_id=interview.process_id,
        interviewer_id=interview.interviewer_id,
        interview_type=interview.interview_type,
        scheduled_datetime=interview.scheduled_datetime.strftime("%Y-%m-%dT%H:%M"),
        duration_minutes=interview.duration_minutes,
        status=interview.status,
        notes=interview.notes,
        cancellation_reason=interview.cancellation_reason,
        reschedule_reason=interview.reschedule_reason,
    )


async def schedule_interview_service(
    input: ScheduleInterviewInput,
) -> ScheduleInterviewOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.interview import create_interview

    try:
        scheduled_dt = datetime.fromisoformat(input.proposed_datetime).replace(
            tzinfo=timezone.utc
        )

        model = InterviewModel(
            process_id=input.process_id,
            candidate_id=input.candidate_id,
            interviewer_id=input.interviewer_id,
            interview_type=input.interview_type,
            scheduled_datetime=scheduled_dt,
            duration_minutes=input.duration_minutes,
            notes=input.notes,
        )

        async with AsyncSessionLocal() as session:
            interview = await create_interview(session, model)

        return ScheduleInterviewOutput(
            interview_id=interview.id,
            candidate_id=interview.candidate_id,
            process_id=interview.process_id,
            scheduled_datetime=interview.scheduled_datetime.strftime("%Y-%m-%dT%H:%M"),
            interviewer_id=interview.interviewer_id,
            status="success",
            message=(
                f"Entrevista agendada com sucesso para {input.proposed_datetime}. "
                f"ID do agendamento: {interview.id}."
            ),
        )
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao agendar entrevista para o candidato {input.candidate_id}: {e}"
        ) from e


async def reschedule_interview_service(
    input: RescheduleInterviewInput,
) -> RescheduleInterviewOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.interview import reschedule_interview as repo_reschedule

    try:
        new_dt = datetime.fromisoformat(input.new_datetime).replace(tzinfo=timezone.utc)

        async with AsyncSessionLocal() as session:
            interview = await repo_reschedule(
                session, input.interview_id, new_dt, input.reason
            )

        previous_dt = interview.scheduled_datetime.strftime("%Y-%m-%dT%H:%M")

        return RescheduleInterviewOutput(
            interview_id=interview.id,
            previous_datetime=previous_dt,
            new_datetime=interview.scheduled_datetime.strftime("%Y-%m-%dT%H:%M"),
            status="success",
            message=(
                f"Entrevista {interview.id} remarcada para "
                f"{interview.scheduled_datetime.strftime('%Y-%m-%dT%H:%M')}. "
                f"Motivo: {input.reason}"
            ),
        )
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao remarcar entrevista {input.interview_id}: {e}"
        ) from e


async def get_available_slots_service(
    input: GetAvailableSlotsInput,
) -> GetAvailableSlotsOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.interview import get_interviewer_slots

    try:
        date_from = datetime.fromisoformat(input.date_from).replace(tzinfo=timezone.utc)
        date_to = datetime.fromisoformat(input.date_to).replace(
            hour=23, minute=59, tzinfo=timezone.utc
        )

        async with AsyncSessionLocal() as session:
            booked = await get_interviewer_slots(
                session, input.interviewer_id, date_from, date_to
            )

        booked_windows = [
            (
                i.scheduled_datetime,
                i.scheduled_datetime + timedelta(minutes=i.duration_minutes),
            )
            for i in booked
        ]

        # Generate candidate slots (09:00-17:00, every hour on business days)
        slots: list[TimeSlot] = []
        current = date_from.replace(hour=9, minute=0, second=0, microsecond=0)
        slot_duration = timedelta(minutes=input.duration_minutes)

        while current <= date_to:
            if current.weekday() < 5 and 9 <= current.hour < 17:
                slot_end = current + slot_duration
                occupied = any(
                    not (slot_end <= bstart or current >= bend)
                    for bstart, bend in booked_windows
                )
                if not occupied:
                    slots.append(
                        TimeSlot(
                            start_datetime=current.strftime("%Y-%m-%dT%H:%M"),
                            end_datetime=slot_end.strftime("%Y-%m-%dT%H:%M"),
                        )
                    )
            current += timedelta(hours=1)

        msg = (
            f"{len(slots)} horário(s) disponível(is) para o entrevistador "
            f"{input.interviewer_id} entre {input.date_from} e {input.date_to}."
            if slots
            else f"Nenhum horário disponível para {input.interviewer_id} no período informado."
        )

        return GetAvailableSlotsOutput(
            interviewer_id=input.interviewer_id,
            available_slots=slots,
            message=msg,
        )
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar horários do entrevistador {input.interviewer_id}: {e}"
        ) from e


async def get_interviews_by_process_service(
    input: GetInterviewsByProcessInput,
) -> GetInterviewsByProcessOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.candidate import get_candidate_by_id
    from db.repositories.interview import list_interviews_by_process

    try:
        async with AsyncSessionLocal() as session:
            rows = await list_interviews_by_process(session, input.process_id)

        details: list[InterviewDetail] = []
        for interview in rows:
            try:
                async with AsyncSessionLocal() as session:
                    candidate = await get_candidate_by_id(session, interview.candidate_id)
                candidate_name = candidate.full_name
            except Exception:
                candidate_name = interview.candidate_id

            details.append(_to_interview_detail(interview, candidate_name))

        total = len(details)
        msg = (
            f"{total} entrevista(s) encontrada(s) para o processo {input.process_id}."
            if total
            else f"Nenhuma entrevista encontrada para o processo {input.process_id}."
        )
        return GetInterviewsByProcessOutput(
            process_id=input.process_id,
            interviews=details,
            total=total,
            message=msg,
        )
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar entrevistas do processo {input.process_id}: {e}"
        ) from e


async def get_interview_service(input: GetInterviewInput) -> GetInterviewOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.candidate import get_candidate_by_id
    from db.repositories.interview import get_interview_by_id

    try:
        async with AsyncSessionLocal() as session:
            interview = await get_interview_by_id(session, input.interview_id)

        try:
            async with AsyncSessionLocal() as session:
                candidate = await get_candidate_by_id(session, interview.candidate_id)
            candidate_name = candidate.full_name
        except Exception:
            candidate_name = interview.candidate_id

        detail = _to_interview_detail(interview, candidate_name)
        return GetInterviewOutput(
            interview=detail,
            message=f"Entrevista {interview.id} recuperada com sucesso.",
        )
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao buscar entrevista {input.interview_id}: {e}"
        ) from e


_INTERVIEW_TYPES: list[InterviewTypeInfo] = [
    InterviewTypeInfo(interview_type="rh",       label="Entrevista RH",          description="Avaliação comportamental e fit cultural conduzida pelo RH."),
    InterviewTypeInfo(interview_type="tecnica",   label="Entrevista Técnica",     description="Avaliação de competências técnicas e resolução de problemas."),
    InterviewTypeInfo(interview_type="cultural",  label="Fit Cultural",           description="Avaliação de alinhamento com os valores e cultura da empresa."),
    InterviewTypeInfo(interview_type="gestao",    label="Entrevista com Gestão",  description="Entrevista com o gestor direto ou liderança executiva."),
]


async def get_scheduling_options_service() -> GetSchedulingOptionsOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.interviewer import list_interviewers

    async with AsyncSessionLocal() as session:
        rows = await list_interviewers(session)

    interviewers = [
        InterviewerInfo(
            interviewer_id=r.id,
            name=r.name,
            role=r.role,
            department=r.department,
        )
        for r in rows
    ]

    return GetSchedulingOptionsOutput(
        interviewers=interviewers,
        interview_types=_INTERVIEW_TYPES,
        message="Entrevistadores e tipos de entrevista disponíveis para agendamento.",
    )


async def cancel_interview_service(
    input: CancelInterviewInput,
) -> CancelInterviewOutput:
    from db.engine import AsyncSessionLocal
    from db.repositories.interview import cancel_interview as repo_cancel

    try:
        async with AsyncSessionLocal() as session:
            interview = await repo_cancel(session, input.interview_id, input.reason)

        return CancelInterviewOutput(
            interview_id=interview.id,
            status="success",
            message=(
                f"Entrevista {interview.id} cancelada com sucesso. Motivo: {input.reason}"
            ),
        )
    except Exception as e:
        raise RecruitmentServiceError(
            f"Falha ao cancelar entrevista {input.interview_id}: {e}"
        ) from e
