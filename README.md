# Recruitment Chatbot

Chatbot de recrutamento e seleção construído com **FastMCP**, **Agno** e **AgentOS**. O agente conversa em linguagem natural com recrutadores para gerenciar vagas, processos seletivos, triagem de candidatos e agendamento de entrevistas.

## Arquitetura

> Diagramas interativos — abra no navegador:
> - **[docs/layers.html](docs/layers.html)** — diagrama de camadas (Frontend → Infra)
> - **[docs/uml-classes.html](docs/uml-classes.html)** — diagrama de classes UML (modelos, atributos, relacionamentos)
> - **[docs/uml-components.html](docs/uml-components.html)** — diagrama de componentes UML (interfaces, dependências, portas)
> - **[docs/architecture.html](docs/architecture.html)** — visão completa com detalhes de todas as camadas

```
┌──────────────────────────────────────────────────────────┐
│           AgentUI  (Next.js :3000)                       │
│  Chat · Widgets (ProcessDashboard, CandidateBoard …)     │
└───────────────────────┬──────────────────────────────────┘
                        │  HTTP / SSE (streaming)
┌───────────────────────▼──────────────────────────────────┐
│           AgentOS  (FastAPI :7777)                        │
│  JWT RBAC · WebSocket streaming · sessões PostgreSQL      │
└───────────────────────┬──────────────────────────────────┘
                        │  MCPTools (Agno)
┌───────────────────────▼──────────────────────────────────┐
│      Recruitment Agent  (Agno + claude-sonnet-4-5)        │
│  7 widgets · histórico de conversas · instruções PT-BR    │
└──────┬───────────┬──────────────┬──────────────┬─────────┘
       │           │    MCP Protocol (streamable-http)
┌──────▼───┐ ┌─────▼──────┐ ┌────▼──────┐ ┌─────▼────────┐
│:8001     │ │:8002        │ │:8003      │ │:8004         │
│job-      │ │process-     │ │candidate- │ │interview-    │
│opening   │ │management   │ │screening  │ │scheduling    │
│5 tools   │ │8 tools      │ │4 tools    │ │7 tools       │
└──────┬───┘ └─────┬──────┘ └────┬──────┘ └─────┬────────┘
       └───────────┴──────────────┴──────────────┘
                        │  chamadas async
┌───────────────────────▼──────────────────────────────────┐
│           Services + Schemas  (services/ · schemas/)      │
│  Lógica de negócio pura · Pydantic v2 · SLA · gargalos   │
└───────────────────────┬──────────────────────────────────┘
                        │  repository pattern
┌───────────────────────▼──────────────────────────────────┐
│           SQLAlchemy 2 + Repositories  (db/)              │
│  AsyncSession · asyncpg · pool_size=5 · Alembic           │
└───────────────────────┬──────────────────────────────────┘
                        │  postgresql+asyncpg://
┌───────────────────────▼──────────────────────────────────┐
│           PostgreSQL 16  (Docker :5432)                   │
│  job_openings · selection_processes · candidates          │
│  interviews · interviewers · process_timeline             │
└──────────────────────────────────────────────────────────┘
```

| Camada | Tecnologia | Porta |
|---|---|---|
| Frontend | Next.js 15 + React 18 + Zustand | :3000 |
| API Gateway | FastAPI (AgentOS) + JWT RBAC | :7777 |
| Agente IA | Agno + Claude Sonnet 4.5 | — |
| Protocolo | MCP via FastMCP 2.0 (streamable-http) | — |
| MCP Servers | 4 instâncias independentes | :8001–:8004 |
| Serviços | Python async (sem framework) | — |
| ORM | SQLAlchemy 2 + asyncpg | — |
| Banco | PostgreSQL 16 (Docker) | :5432 |
| Admin DB | pgAdmin 4 (Docker) | :5050 |

## Pré-requisitos

| Ferramenta | Versão mínima |
|---|---|
| Python | 3.11+ |
| [uv](https://docs.astral.sh/uv/) | latest |
| Docker + Docker Compose | 24+ |
| Node.js / pnpm | 18+ / 9+ (frontend) |

## Configuração

### 1. Clone e instale as dependências

```bash
git clone <repo-url>
cd ia-recruitment

# dependências de produção
make install

# dependências de desenvolvimento (pytest, ruff)
make install-dev
```

### 2. Configure as variáveis de ambiente

Copie o arquivo de exemplo e preencha os valores:

```bash
cp .env.example .env
```

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL de conexão PostgreSQL |
| `ANTHROPIC_API_KEY` | Chave de API do Claude (Anthropic) |
| `CORS_ALLOWED_ORIGINS` | Origins permitidas pelo AgentOS |
| `JOB_OPENING_SERVER_URL` | URL do MCP server de abertura de vagas |
| `PROCESS_MANAGEMENT_SERVER_URL` | URL do MCP server de processos |
| `SCREENING_SERVER_URL` | URL do MCP server de triagem |
| `SCHEDULING_SERVER_URL` | URL do MCP server de agendamento |
| `SLA_ALERT_THRESHOLD_DAYS` | Dias antes do vencimento do SLA para alertar (padrão: 2) |

### 3. Suba o banco de dados

```bash
make db-up
```

PostgreSQL estará disponível em `localhost:5432`.  
pgAdmin em `http://localhost:5050`.

### 4. Execute as migrações

```bash
make migrate
```

Para popular o banco com dados fictícios:

```bash
make seed
```

## Executando

### Backend (MCP servers + AgentOS)

```bash
make start
```

Isso sobe os quatro MCP servers e o AgentOS em sequência:

| Serviço | URL |
|---|---|
| AgentOS API | `http://localhost:7777` |
| job-opening MCP | `http://localhost:8001/mcp` |
| process-management MCP | `http://localhost:8002/mcp` |
| candidate-screening MCP | `http://localhost:8003/mcp` |
| interview-scheduling MCP | `http://localhost:8004/mcp` |

Para encerrar: `make stop`  
Para reiniciar: `make restart`

### Frontend (AgentUI)

```bash
cd agent-ui
pnpm install
pnpm dev
```

A interface estará disponível em `http://localhost:3000`.  
Configure o endpoint do AgentOS no sidebar do AgentUI para `http://localhost:7777`.

## Estrutura do projeto

```
ia-recruitment/
├── agentos.py                      # Entrypoint da API de produção (AgentOS)
├── agents/
│   └── recruitment_agent.py        # Agente principal com MCPTools
├── tools/                          # FastMCP servers (um por domínio)
│   ├── job_opening_server.py
│   ├── process_management_server.py
│   ├── candidate_screening_server.py
│   └── interview_scheduling_server.py
├── schemas/                        # Modelos Pydantic v2 de input/output
│   ├── job_opening.py
│   ├── process.py
│   ├── candidate.py
│   └── scheduling.py
├── services/                       # Lógica de negócio (sem imports de framework)
│   ├── job_opening.py
│   ├── process_management.py
│   ├── candidate_screening.py
│   └── interview_scheduling.py
├── db/                             # Modelos SQLAlchemy e configuração de DB
├── alembic/                        # Migrações de banco de dados
├── utils/
│   ├── config.py                   # Settings via pydantic-settings
│   ├── exceptions.py               # Exceções tipadas do domínio
│   └── logging.py
├── tests/                          # Espelha a estrutura de src/
│   ├── tools/
│   └── services/
├── agent-ui/                       # Frontend Next.js (AgentUI)
├── scripts/
│   └── seed.py                     # Seed de dados fictícios
├── docker-compose.yml              # PostgreSQL + pgAdmin
├── Makefile                        # Comandos de desenvolvimento
├── pyproject.toml
└── start.sh                        # Script para subir todos os serviços
```

## Comandos disponíveis

```bash
# Ambiente
make install           # Instala dependências de produção
make install-dev       # Instala dependências + dev (pytest, ruff)

# Banco de dados
make db-up             # Sobe PostgreSQL + pgAdmin via Docker
make db-down           # Para e remove os containers
make db-stop           # Para os containers (mantém volumes)
make db-reset          # Remove volumes e recria do zero
make db-shell          # Abre psql no container

# Migrações
make migrate           # Aplica todas as migrations pendentes
make migrate-auto      # Gera nova migration pelo autogenerate
make migrate-history   # Exibe histórico de migrations
make migrate-rollback  # Reverte a última migration
make seed              # Popula o banco com dados fictícios

# Servidores
make start             # Sobe MCP servers (8001–8004) + AgentOS (7777)
make stop              # Encerra todos os serviços
make restart           # stop + start
make status            # Mostra portas em uso

# Testes
make test              # Roda todos os testes
make test-verbose      # Testes com output detalhado
make test-services     # Apenas testes de services/
make test-tools        # Apenas testes de tools/
make test-cov          # Testes com relatório de cobertura

# Qualidade de código
make lint              # Verifica problemas com ruff
make format            # Formata código com ruff
make fix               # lint + format automático
make check             # Lint + verificação de imports
```

## Testes

```bash
make test
```

Os testes usam `pytest-asyncio` (modo `auto`) e `pytest-mock`. Cada MCP tool deve ter cobertura para: caminho feliz, input inválido e falha de serviço.

## Qualidade de código

O projeto usa `ruff` como formatter e linter:

```bash
make fix   # corrige e formata em um só comando
```

Regras ativas: `E, F, I, UP, B, SIM` · comprimento de linha: 88.

## Migrações de banco

```bash
# Criar nova migration a partir dos modelos SQLAlchemy
make migrate-auto

# Aplicar pendentes
make migrate

# Reverter a última
make migrate-rollback
```
