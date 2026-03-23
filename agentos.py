from dotenv import load_dotenv

load_dotenv()

from contextlib import asynccontextmanager
from typing import Optional

from agno.db.postgres import PostgresDb
from agno.os.app import AgentOS
from fastapi import FastAPI, HTTPException, Query

from agents.recruitment_agent import recruitment_agent
from db.engine import create_tables
from schemas.process import GetProcessDetailInput, ListProcessesInput, ProcessStatus, SLAStatus
from services.process_management import get_process_detail_service, list_processes_service
from utils.config import settings
from utils.exceptions import ProcessNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


agno_db = PostgresDb(db_url=settings.database_url)

agent_os = AgentOS(
    name="Recruitment AgentOS",
    agents=[recruitment_agent],
    db=agno_db,
    cors_allowed_origins=settings.cors_allowed_origins,
    tracing=False,
    lifespan=lifespan,
)

app = agent_os.get_app()


@app.get("/api/processes")
async def api_list_processes(
    status_filter: Optional[str] = Query(None),
    sla_filter: Optional[str] = Query(None),
    recruiter_id: Optional[str] = Query(None),
):
    try:
        input_data = ListProcessesInput(
            status_filter=ProcessStatus(status_filter) if status_filter else None,
            sla_filter=SLAStatus(sla_filter) if sla_filter else None,
            recruiter_id=recruiter_id,
        )
        result = await list_processes_service(input_data)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/processes/{process_id}")
async def api_get_process(process_id: str):
    try:
        result = await get_process_detail_service(
            GetProcessDetailInput(process_id=process_id)
        )
        return result.model_dump()
    except ProcessNotFoundError:
        raise HTTPException(status_code=404, detail=f"Processo {process_id} não encontrado")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    agent_os.serve(app="agentos:app", host="0.0.0.0", port=7777, reload=False)
