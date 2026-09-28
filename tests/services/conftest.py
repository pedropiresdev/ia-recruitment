import uuid

import pytest

from db.engine import AsyncSessionLocal
from db.models.process import SelectionProcessModel
from db.repositories.process import create_process


@pytest.fixture
async def process_id():
    """Cria um processo seletivo isolado no banco de testes."""
    pid = f"PROC-T{uuid.uuid4().hex[:6].upper()}"
    async with AsyncSessionLocal() as session:
        await create_process(
            session,
            SelectionProcessModel(
                id=pid,
                job_title="Engenheiro de Testes",
                department="Qualidade",
                recruiter_name="CI Pipeline",
            ),
        )
    return pid
