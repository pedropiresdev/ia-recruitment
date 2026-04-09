from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "recruitment-agentos"
    debug: bool = False
    database_url: str = "postgresql://admin:admin123@localhost:5432/recruitment"
    cors_allowed_origins: List[str] = ["http://localhost:3000"]

    anthropic_api_key: Optional[str] = None

    # URLs dos servidores MCP — um por domínio
    job_opening_server_url: str = "http://localhost:8001/mcp"
    process_management_server_url: str = "http://localhost:8002/mcp"
    screening_server_url: str = "http://localhost:8003/mcp"
    scheduling_server_url: str = "http://localhost:8004/mcp"

    # URL do orchestrator MCP server (exposto para a LiGiaPro)
    orchestrator_server_url: str = "http://localhost:8000/mcp"

    # Configuração de SLA
    sla_alert_threshold_days: int = 2


settings = Settings()
