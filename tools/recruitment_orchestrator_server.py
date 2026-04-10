from agno.db.postgres import PostgresDb
from fastmcp import FastMCP

from agents.recruitment_agent import make_recruitment_agent
from utils.config import settings

mcp = FastMCP(name="recruitment-orchestrator")

# Storage dedicado para sessões do orchestrator (separado do AgentOS).
_db = PostgresDb(
    db_url=settings.database_url,
    session_table="orchestrator_sessions",
)

_agent = make_recruitment_agent(db=_db, use_widgets=False)


@mcp.tool()
async def handle_recruitment_message(message: str, session_id: str) -> str:
    """
    Processa uma mensagem em linguagem natural para o agente de recrutamento.

    Mantém histórico de conversa por session_id — use o identificador do usuário
    ou da conversa na LiGiaPro para garantir continuidade entre mensagens.

    A resposta é retornada em texto markdown puro, sem blocos JSON de widget,
    adequada para renderização em interfaces de chat como Webchat, WhatsApp e Teams.

    Args:
        message: Mensagem do usuário em linguagem natural (PT-BR).
        session_id: Identificador único da sessão/conversa (ex: user_id da LiGiaPro).

    Returns:
        Resposta do agente em markdown sem widgets JSON.
    """
    response = await _agent.arun(message, session_id=session_id)
    return response.get_content_as_string()
