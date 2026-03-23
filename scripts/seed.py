"""
Script de seed — popula o banco com dados fictícios de recrutamento.
Uso: uv run python scripts/seed.py
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Garante que o root do projeto está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import text

from db.engine import AsyncSessionLocal, engine
from db.models.candidate import CandidateModel
from db.models.interview import InterviewModel
from db.models.interviewer import InterviewerModel
from db.models.job_opening import JobOpeningModel
from db.models.process import ProcessTimelineModel, SelectionProcessModel

# ─── Helpers ──────────────────────────────────────────────────────────────────

def utc(days_offset: int = 0, hours: int = 0) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days_offset, hours=hours)


def past(days: int) -> datetime:
    return utc(-days)


# ─── Dados fictícios ──────────────────────────────────────────────────────────

JOB_OPENINGS = [
    {
        "id": "OPEN-A1B2C3D4",
        "job_posting_id": "JOB-A1B2C3D4",
        "position_title": "Head de Produto",
        "department": "Produto",
        "seniority_level": "Gestão",
        "deadline_days": 45,
        "requirements": "Experiência com roadmap, OKRs, squads e stakeholders executivos. "
                        "Sólido background em produtos digitais B2B.",
        "salary_range": "R$25.000 - R$35.000",
        "requestor_name": "Rodrigo Andrade",
        "job_description_draft": (
            "# Head de Produto — Gestão\n\n"
            "**Departamento:** Produto\n\n"
            "## Sobre a Vaga\n"
            "Buscamos um Head de Produto para liderar nossas squads de produto digital, "
            "com foco em crescimento e retenção de clientes B2B.\n\n"
            "## Requisitos\n"
            "- Experiência prévia como Head de Produto ou Diretor de Produto\n"
            "- Domínio de metodologias ágeis e OKRs\n"
            "- Habilidade de comunicação com C-level\n\n"
            "## Remuneração\nR$25.000 - R$35.000\n\n"
            "*Prazo para preenchimento: 45 dias*"
        ),
        "approved": True,
    },
    {
        "id": "OPEN-E5F6G7H8",
        "job_posting_id": "JOB-E5F6G7H8",
        "position_title": "Engenheiro de Dados Sênior",
        "department": "Dados & Analytics",
        "seniority_level": "Sênior",
        "deadline_days": 30,
        "requirements": "Python, Spark, dbt, Airflow, cloud (AWS ou GCP). "
                        "Experiência com pipelines de dados em produção.",
        "salary_range": "R$18.000 - R$24.000",
        "requestor_name": "Camila Torres",
        "job_description_draft": (
            "# Engenheiro de Dados Sênior\n\n"
            "**Departamento:** Dados & Analytics\n\n"
            "## Sobre a Vaga\n"
            "Vaga para engenheiro sênior responsável por arquitetura e manutenção "
            "dos pipelines de dados da empresa.\n\n"
            "## Requisitos\nPython, Spark, dbt, Airflow, AWS/GCP.\n\n"
            "## Remuneração\nR$18.000 - R$24.000\n\n"
            "*Prazo para preenchimento: 30 dias*"
        ),
        "approved": True,
    },
    {
        "id": "OPEN-I9J0K1L2",
        "job_posting_id": "JOB-I9J0K1L2",
        "position_title": "Analista de RH Pleno",
        "department": "Recursos Humanos",
        "seniority_level": "Pleno",
        "deadline_days": 20,
        "requirements": "Experiência em recrutamento e seleção, DHO e cultura organizacional.",
        "salary_range": "R$6.000 - R$9.000",
        "requestor_name": "Fernanda Costa",
        "job_description_draft": (
            "# Analista de RH Pleno\n\n"
            "**Departamento:** Recursos Humanos\n\n"
            "## Sobre a Vaga\n"
            "Analista para apoiar processos de R&S, onboarding e iniciativas de cultura.\n\n"
            "## Requisitos\nFormação em Psicologia, ADM ou RH. Experiência com ATS.\n\n"
            "## Remuneração\nR$6.000 - R$9.000\n\n"
            "*Prazo para preenchimento: 20 dias*"
        ),
        "approved": True,
    },
    {
        "id": "OPEN-M3N4O5P6",
        "job_posting_id": "JOB-M3N4O5P6",
        "position_title": "Product Manager",
        "department": "Produto",
        "seniority_level": "Pleno",
        "deadline_days": 60,
        "requirements": "Experiência com discovery, testes A/B e métricas de produto.",
        "salary_range": "R$14.000 - R$18.000",
        "requestor_name": "Rodrigo Andrade",
        "job_description_draft": (
            "# Product Manager — Pleno\n\n"
            "**Departamento:** Produto\n\n"
            "## Sobre a Vaga\n"
            "PM para atuar em squad de growth, liderando iniciativas de aquisição e ativação.\n\n"
            "## Requisitos\nDiscovery, A/B tests, SQL básico, comunicação com engenharia.\n\n"
            "## Remuneração\nR$14.000 - R$18.000\n\n"
            "*Prazo para preenchimento: 60 dias*"
        ),
        "approved": False,
    },
    {
        "id": "OPEN-Q7R8S9T0",
        "job_posting_id": "JOB-Q7R8S9T0",
        "position_title": "Tech Lead Backend",
        "department": "Engenharia",
        "seniority_level": "Sênior",
        "deadline_days": 35,
        "requirements": "Python ou Go, arquitetura de microsserviços, liderança técnica de times.",
        "salary_range": "R$20.000 - R$28.000",
        "requestor_name": "Lucas Rocha",
        "job_description_draft": (
            "# Tech Lead Backend — Sênior\n\n"
            "**Departamento:** Engenharia\n\n"
            "## Sobre a Vaga\n"
            "Tech Lead para liderar time de backend em ambiente de alta escala.\n\n"
            "## Requisitos\nPython/Go, microsserviços, Kubernetes, mentoria técnica.\n\n"
            "## Remuneração\nR$20.000 - R$28.000\n\n"
            "*Prazo para preenchimento: 35 dias*"
        ),
        "approved": True,
    },
]

INTERVIEWERS = [
    {"id": "REC-001", "name": "Mariana Silva",  "role": "Recrutadora Sênior",    "department": "RH",                  "email": "mariana.silva@empresa.com"},
    {"id": "REC-002", "name": "Carlos Mendes",  "role": "Recrutador Sênior",     "department": "RH",                  "email": "carlos.mendes@empresa.com"},
    {"id": "REC-003", "name": "Fernanda Costa", "role": "Analista de RH",        "department": "RH",                  "email": "fernanda.costa@empresa.com"},
    {"id": "EXE-001", "name": "Lucas Rocha",    "role": "CTO",                   "department": "Engenharia",           "email": "lucas.rocha@empresa.com"},
    {"id": "EXE-002", "name": "Rodrigo Andrade","role": "Head de Produto",        "department": "Produto",              "email": "rodrigo.andrade@empresa.com"},
    {"id": "EXE-003", "name": "Camila Torres",  "role": "Head de Dados",          "department": "Dados & Analytics",   "email": "camila.torres@empresa.com"},
]

PROCESSES = [
    {
        "id": "PROC-001",
        "opening_id": "OPEN-A1B2C3D4",
        "job_title": "Head de Produto",
        "department": "Produto",
        "recruiter_name": "Mariana Silva",
        "recruiter_id": "REC-001",
        "status": "em_andamento",
        "sla_status": "em_atraso",
        "sla_deadline_date": past(8),
        "open_candidates_count": 5,
        "created_at": past(53),
        "updated_at": past(12),
    },
    {
        "id": "PROC-002",
        "opening_id": "OPEN-E5F6G7H8",
        "job_title": "Engenheiro de Dados Sênior",
        "department": "Dados & Analytics",
        "recruiter_name": "Carlos Mendes",
        "recruiter_id": "REC-002",
        "status": "em_andamento",
        "sla_status": "em_risco",
        "sla_deadline_date": utc(2),
        "open_candidates_count": 8,
        "created_at": past(28),
        "updated_at": past(3),
    },
    {
        "id": "PROC-003",
        "opening_id": "OPEN-I9J0K1L2",
        "job_title": "Analista de RH Pleno",
        "department": "Recursos Humanos",
        "recruiter_name": "Fernanda Costa",
        "recruiter_id": "REC-003",
        "status": "em_aberto",
        "sla_status": "no_prazo",
        "sla_deadline_date": utc(18),
        "open_candidates_count": 12,
        "created_at": past(2),
        "updated_at": past(1),
    },
    {
        "id": "PROC-004",
        "opening_id": "OPEN-M3N4O5P6",
        "job_title": "Product Manager",
        "department": "Produto",
        "recruiter_name": "Mariana Silva",
        "recruiter_id": "REC-001",
        "status": "suspenso",
        "sla_status": "no_prazo",
        "sla_deadline_date": utc(40),
        "suspension_reason": "Congelamento de headcount aprovado pelo CFO para o Q2.",
        "open_candidates_count": 0,
        "created_at": past(30),
        "updated_at": past(20),
    },
    {
        "id": "PROC-005",
        "opening_id": "OPEN-Q7R8S9T0",
        "job_title": "Tech Lead Backend",
        "department": "Engenharia",
        "recruiter_name": "Carlos Mendes",
        "recruiter_id": "REC-002",
        "status": "em_andamento",
        "sla_status": "em_atraso",
        "sla_deadline_date": past(3),
        "open_candidates_count": 3,
        "created_at": past(38),
        "updated_at": past(5),
    },
]

TIMELINE_EVENTS = [
    # PROC-001 — Head de Produto (em atraso, 53 dias)
    {"process_id": "PROC-001", "stage": "Abertura da vaga",          "actor": "Mariana Silva",  "event_date": past(53), "notes": "Vaga aprovada pelo board."},
    {"process_id": "PROC-001", "stage": "Publicação no ATS",         "actor": "Mariana Silva",  "event_date": past(50), "notes": None},
    {"process_id": "PROC-001", "stage": "Triagem de currículos",     "actor": "Mariana Silva",  "event_date": past(42), "notes": "47 inscritos, 8 aprovados na triagem."},
    {"process_id": "PROC-001", "stage": "Entrevista RH",             "actor": "Mariana Silva",  "event_date": past(35), "notes": "5 candidatos seguiram para entrevista técnica."},
    {"process_id": "PROC-001", "stage": "Entrevista técnica",        "actor": "Rodrigo Andrade","event_date": past(20), "notes": "Gestor não respondeu sobre os candidatos. Aguardando feedback há 12 dias."},

    # PROC-002 — Engenheiro de Dados Sênior (em risco, 28 dias)
    {"process_id": "PROC-002", "stage": "Abertura da vaga",          "actor": "Carlos Mendes",  "event_date": past(28), "notes": None},
    {"process_id": "PROC-002", "stage": "Publicação no ATS",         "actor": "Carlos Mendes",  "event_date": past(26), "notes": None},
    {"process_id": "PROC-002", "stage": "Triagem de currículos",     "actor": "Carlos Mendes",  "event_date": past(18), "notes": "32 inscritos, 10 aprovados."},
    {"process_id": "PROC-002", "stage": "Entrevista RH",             "actor": "Carlos Mendes",  "event_date": past(10), "notes": "8 candidatos seguiram."},
    {"process_id": "PROC-002", "stage": "Desafio técnico",           "actor": "Camila Torres",  "event_date": past(4),  "notes": "Aguardando avaliação de 6 desafios enviados."},

    # PROC-003 — Analista de RH (no prazo, 2 dias)
    {"process_id": "PROC-003", "stage": "Abertura da vaga",          "actor": "Fernanda Costa", "event_date": past(2),  "notes": None},
    {"process_id": "PROC-003", "stage": "Publicação no ATS",         "actor": "Fernanda Costa", "event_date": past(1),  "notes": "12 inscrições nas primeiras 24h."},

    # PROC-005 — Tech Lead Backend (em atraso, 38 dias)
    {"process_id": "PROC-005", "stage": "Abertura da vaga",          "actor": "Carlos Mendes",  "event_date": past(38), "notes": None},
    {"process_id": "PROC-005", "stage": "Publicação no ATS",         "actor": "Carlos Mendes",  "event_date": past(36), "notes": None},
    {"process_id": "PROC-005", "stage": "Triagem de currículos",     "actor": "Carlos Mendes",  "event_date": past(28), "notes": "21 inscritos, 5 aprovados."},
    {"process_id": "PROC-005", "stage": "Entrevista RH",             "actor": "Carlos Mendes",  "event_date": past(20), "notes": "3 seguiram."},
    {"process_id": "PROC-005", "stage": "Entrevista técnica",        "actor": "Lucas Rocha",    "event_date": past(12), "notes": "1 candidato reprovado, 2 aguardam entrevista com CTO."},
    {"process_id": "PROC-005", "stage": "Entrevista com CTO",        "actor": "Lucas Rocha",    "event_date": past(5),  "notes": "CTO em viagem, entrevista não realizada. Reagendamento pendente."},
]

CANDIDATES = [
    # PROC-001 — Head de Produto
    {"id": "CAND-0001", "process_id": "PROC-001", "full_name": "Ana Paula Ramos",      "email": "ana.ramos@email.com",      "phone": "11 98765-4321", "current_stage": "entrevista", "days_in_stage": 12, "screening_recommendation": "aprovar", "applied_at": past(42)},
    {"id": "CAND-0002", "process_id": "PROC-001", "full_name": "Bruno Carvalho",        "email": "bruno.carvalho@email.com", "phone": "11 91234-5678", "current_stage": "entrevista", "days_in_stage": 12, "screening_recommendation": "aprovar", "applied_at": past(41)},
    {"id": "CAND-0003", "process_id": "PROC-001", "full_name": "Carla Mendonça",        "email": "carla.m@email.com",        "phone": "21 99876-5432", "current_stage": "entrevista", "days_in_stage": 12, "screening_recommendation": "aprovar", "applied_at": past(40)},
    {"id": "CAND-0004", "process_id": "PROC-001", "full_name": "Diego Ferreira",        "email": "diego.f@email.com",        "phone": "11 97654-3210", "current_stage": "entrevista", "days_in_stage": 12, "screening_recommendation": "aprovar", "applied_at": past(39)},
    {"id": "CAND-0005", "process_id": "PROC-001", "full_name": "Elaine Souza",          "email": "elaine.s@email.com",       "phone": "31 98888-7777", "current_stage": "entrevista", "days_in_stage": 12, "screening_recommendation": "aprovar", "applied_at": past(38)},

    # PROC-002 — Engenheiro de Dados Sênior
    {"id": "CAND-0006", "process_id": "PROC-002", "full_name": "Felipe Nunes",          "email": "felipe.nunes@email.com",   "phone": "11 94321-8765", "current_stage": "tecnico",    "days_in_stage": 4,  "screening_recommendation": "aprovar", "applied_at": past(18)},
    {"id": "CAND-0007", "process_id": "PROC-002", "full_name": "Gabriela Lima",         "email": "gabi.lima@email.com",      "phone": "21 93333-2222", "current_stage": "tecnico",    "days_in_stage": 4,  "screening_recommendation": "aprovar", "applied_at": past(17)},
    {"id": "CAND-0008", "process_id": "PROC-002", "full_name": "Henrique Castro",       "email": "h.castro@email.com",       "phone": "11 92222-1111", "current_stage": "tecnico",    "days_in_stage": 4,  "screening_recommendation": "aprovar", "applied_at": past(16)},
    {"id": "CAND-0009", "process_id": "PROC-002", "full_name": "Isabela Martins",       "email": "isa.martins@email.com",    "phone": "41 98765-1234", "current_stage": "tecnico",    "days_in_stage": 4,  "screening_recommendation": "aprovar", "applied_at": past(15)},
    {"id": "CAND-0010", "process_id": "PROC-002", "full_name": "João Almeida",          "email": "joao.almeida@email.com",   "phone": "11 91111-0000", "current_stage": "entrevista", "days_in_stage": 10, "screening_recommendation": "aprovar", "applied_at": past(18)},
    {"id": "CAND-0011", "process_id": "PROC-002", "full_name": "Karen Oliveira",        "email": "karen.o@email.com",        "phone": "51 99999-8888", "current_stage": "entrevista", "days_in_stage": 10, "screening_recommendation": "aprovar", "applied_at": past(17)},
    {"id": "CAND-0012", "process_id": "PROC-002", "full_name": "Leonardo Pires",        "email": "leo.pires@email.com",      "phone": "11 98888-6666", "current_stage": "reprovado",  "days_in_stage": 14, "screening_recommendation": "reprovar", "applied_at": past(18)},
    {"id": "CAND-0013", "process_id": "PROC-002", "full_name": "Mariana Gomes",         "email": "mari.gomes@email.com",     "phone": "21 97777-5555", "current_stage": "tecnico",    "days_in_stage": 4,  "screening_recommendation": "aprovar", "applied_at": past(16)},
    {"id": "CAND-0014", "process_id": "PROC-002", "full_name": "Nelson Ribeiro",        "email": "nelson.r@email.com",       "phone": "11 96666-4444", "current_stage": "tecnico",    "days_in_stage": 4,  "screening_recommendation": "aprovar", "applied_at": past(15)},

    # PROC-003 — Analista de RH (triagem inicial)
    {"id": "CAND-0015", "process_id": "PROC-003", "full_name": "Olivia Santos",         "email": "olivia.s@email.com",       "phone": "11 95555-3333", "current_stage": "inscrito",   "days_in_stage": 1,  "screening_recommendation": None, "applied_at": past(1)},
    {"id": "CAND-0016", "process_id": "PROC-003", "full_name": "Paulo Rodrigues",       "email": "paulo.r@email.com",        "phone": "21 94444-2222", "current_stage": "inscrito",   "days_in_stage": 1,  "screening_recommendation": None, "applied_at": past(1)},
    {"id": "CAND-0017", "process_id": "PROC-003", "full_name": "Queila Barros",         "email": "queila.b@email.com",       "phone": "31 93333-1111", "current_stage": "inscrito",   "days_in_stage": 1,  "screening_recommendation": None, "applied_at": past(1)},
    {"id": "CAND-0018", "process_id": "PROC-003", "full_name": "Rafael Teixeira",       "email": "rafael.t@email.com",       "phone": "11 92222-0000", "current_stage": "triagem",    "days_in_stage": 1,  "screening_recommendation": None, "applied_at": past(2)},
    {"id": "CAND-0019", "process_id": "PROC-003", "full_name": "Sabrina Monteiro",      "email": "sabrina.m@email.com",      "phone": "41 91111-9999", "current_stage": "triagem",    "days_in_stage": 1,  "screening_recommendation": None, "applied_at": past(2)},

    # PROC-005 — Tech Lead Backend
    {"id": "CAND-0020", "process_id": "PROC-005", "full_name": "Thiago Cunha",          "email": "thiago.cunha@email.com",   "phone": "11 90000-8888", "current_stage": "gestao",     "days_in_stage": 5,  "screening_recommendation": "aprovar", "applied_at": past(28)},
    {"id": "CAND-0021", "process_id": "PROC-005", "full_name": "Ursula Freitas",        "email": "ursula.f@email.com",       "phone": "21 98765-0000", "current_stage": "gestao",     "days_in_stage": 5,  "screening_recommendation": "aprovar", "applied_at": past(27)},
    {"id": "CAND-0022", "process_id": "PROC-005", "full_name": "Victor Nascimento",     "email": "victor.n@email.com",       "phone": "11 97654-9999", "current_stage": "reprovado",  "days_in_stage": 12, "screening_recommendation": "reprovar", "applied_at": past(28)},
]

INTERVIEWS = [
    # PROC-001 — Entrevistas com gestor (aguardando feedback)
    {"id": "INT-0001", "process_id": "PROC-001", "candidate_id": "CAND-0001", "interviewer_id": "REC-001", "interview_type": "gestao",   "scheduled_datetime": past(12), "status": "realizada", "notes": "Feedback pendente do gestor Rodrigo Andrade."},
    {"id": "INT-0002", "process_id": "PROC-001", "candidate_id": "CAND-0002", "interviewer_id": "REC-001", "interview_type": "gestao",   "scheduled_datetime": past(12), "status": "realizada", "notes": "Feedback pendente."},
    {"id": "INT-0003", "process_id": "PROC-001", "candidate_id": "CAND-0003", "interviewer_id": "REC-001", "interview_type": "gestao",   "scheduled_datetime": past(11), "status": "realizada", "notes": "Feedback pendente."},
    {"id": "INT-0004", "process_id": "PROC-001", "candidate_id": "CAND-0004", "interviewer_id": "REC-001", "interview_type": "gestao",   "scheduled_datetime": past(11), "status": "realizada", "notes": "Feedback pendente."},
    {"id": "INT-0005", "process_id": "PROC-001", "candidate_id": "CAND-0005", "interviewer_id": "REC-001", "interview_type": "gestao",   "scheduled_datetime": past(10), "status": "realizada", "notes": "Feedback pendente."},

    # PROC-002 — Desafio técnico enviado
    {"id": "INT-0006", "process_id": "PROC-002", "candidate_id": "CAND-0006", "interviewer_id": "REC-002", "interview_type": "tecnica",  "scheduled_datetime": past(4),  "status": "agendada",  "notes": "Prazo de entrega do desafio: amanhã."},
    {"id": "INT-0007", "process_id": "PROC-002", "candidate_id": "CAND-0007", "interviewer_id": "REC-002", "interview_type": "tecnica",  "scheduled_datetime": past(4),  "status": "agendada",  "notes": "Prazo de entrega do desafio: amanhã."},

    # PROC-005 — Entrevista com CTO cancelada
    {"id": "INT-0008", "process_id": "PROC-005", "candidate_id": "CAND-0020", "interviewer_id": "EXE-001", "interview_type": "gestao",   "scheduled_datetime": past(5),  "status": "cancelada", "cancellation_reason": "CTO em viagem corporativa. Reagendamento pendente.", "reschedule_reason": None},
    {"id": "INT-0009", "process_id": "PROC-005", "candidate_id": "CAND-0021", "interviewer_id": "EXE-001", "interview_type": "gestao",   "scheduled_datetime": past(5),  "status": "cancelada", "cancellation_reason": "CTO em viagem corporativa. Reagendamento pendente.", "reschedule_reason": None},

    # Próximas entrevistas agendadas (PROC-002)
    {"id": "INT-0010", "process_id": "PROC-002", "candidate_id": "CAND-0010", "interviewer_id": "REC-002", "interview_type": "rh",       "scheduled_datetime": utc(1, hours=10), "status": "agendada", "notes": "Entrevista comportamental."},
    {"id": "INT-0011", "process_id": "PROC-002", "candidate_id": "CAND-0011", "interviewer_id": "REC-002", "interview_type": "rh",       "scheduled_datetime": utc(1, hours=14), "status": "agendada", "notes": "Entrevista comportamental."},
]


# ─── Seed ─────────────────────────────────────────────────────────────────────

async def clear_tables(session) -> None:
    print("  Limpando tabelas existentes...")
    await session.execute(text("DELETE FROM interviews"))
    await session.execute(text("DELETE FROM process_timeline"))
    await session.execute(text("DELETE FROM candidates"))
    await session.execute(text("DELETE FROM selection_processes"))
    await session.execute(text("DELETE FROM job_openings"))
    await session.execute(text("DELETE FROM interviewers"))
    await session.commit()


async def seed_interviewers(session) -> None:
    print(f"  Inserindo {len(INTERVIEWERS)} entrevistadores...")
    for data in INTERVIEWERS:
        session.add(InterviewerModel(**data))
    await session.commit()


async def seed_job_openings(session) -> None:
    print(f"  Inserindo {len(JOB_OPENINGS)} aberturas de posição...")
    for data in JOB_OPENINGS:
        session.add(JobOpeningModel(**data))
    await session.commit()


async def seed_processes(session) -> None:
    print(f"  Inserindo {len(PROCESSES)} processos seletivos...")
    for data in PROCESSES:
        session.add(SelectionProcessModel(**data))
    await session.commit()


async def seed_timeline(session) -> None:
    print(f"  Inserindo {len(TIMELINE_EVENTS)} eventos de timeline...")
    for data in TIMELINE_EVENTS:
        session.add(ProcessTimelineModel(**data))
    await session.commit()


async def seed_candidates(session) -> None:
    print(f"  Inserindo {len(CANDIDATES)} candidatos...")
    for data in CANDIDATES:
        stage_updated_at = data.pop("applied_at")
        applied_at = stage_updated_at
        session.add(CandidateModel(**data, applied_at=applied_at, stage_updated_at=stage_updated_at))
    await session.commit()


async def seed_interviews(session) -> None:
    print(f"  Inserindo {len(INTERVIEWS)} entrevistas...")
    for data in INTERVIEWS:
        data.setdefault("cancellation_reason", None)
        data.setdefault("reschedule_reason", None)
        data.setdefault("notes", None)
        session.add(InterviewModel(**data, duration_minutes=60))
    await session.commit()


async def main() -> None:
    print("\nIniciando seed do banco de dados...\n")

    async with AsyncSessionLocal() as session:
        await clear_tables(session)
        await seed_interviewers(session)
        await seed_job_openings(session)
        await seed_processes(session)
        await seed_timeline(session)
        await seed_candidates(session)
        await seed_interviews(session)

    await engine.dispose()

    print("\nSeed concluído com sucesso!")
    print(f"  {len(INTERVIEWERS)} entrevistadores")
    print("  5 aberturas de posição")
    print("  5 processos seletivos (2 em atraso, 1 em risco, 1 no prazo, 1 suspenso)")
    print(" 22 candidatos distribuídos por etapa")
    print(" 11 entrevistas (realizadas, agendadas e canceladas)")
    print(" 17 eventos de timeline\n")


if __name__ == "__main__":
    asyncio.run(main())
