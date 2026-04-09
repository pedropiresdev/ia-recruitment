# Recruitment Chatbot

Chatbot de recrutamento e seleção construído com **FastMCP**, **Agno** e **AgentOS**. O agente conversa em linguagem natural com recrutadores para gerenciar vagas, processos seletivos, triagem de candidatos e agendamento de entrevistas.

## Dores que resolve

O processo de recrutamento e seleção é tipicamente fragmentado em múltiplas ferramentas — planilhas, e-mails, ATS corporativos, calendários e chats — o que gera gargalos, perda de contexto e retrabalho para o recrutador. Este chatbot centraliza toda a operação em uma única conversa em linguagem natural.

| Dor | Como o chatbot resolve |
|---|---|
| **Vagas gerenciadas em planilhas** | Abertura, atualização e encerramento de vagas diretamente no chat, com histórico persistido em banco |
| **Ausência de visibilidade do pipeline** | Dashboard em tempo real (widget `ProcessDashboard`) exibido na conversa, com estágios, candidatos por fase e alertas de SLA |
| **Triagem manual de currículos** | O agente avalia candidatos cadastrados e avança ou rejeita com justificativa, reduzindo decisões manuais repetitivas |
| **Agendamento caótico de entrevistas** | Verificação de disponibilidade de entrevistadores, criação de slots e notificação automática — tudo pelo chat |
| **SLAs de processos perdidos** | Alerta configurável (`SLA_ALERT_THRESHOLD_DAYS`) quando um processo seletivo se aproxima do prazo limite |
| **Troca constante de sistemas** | Interface única integrada a WhatsApp, Teams ou Webchat via protocolo MCP (ecossistema LiGiaPro) |
| **Onboarding lento de recrutadores** | Linguagem natural em PT-BR elimina curva de aprendizado de ferramentas complexas |

## Funcionalidades

### Gestão de Vagas (`job-opening` · porta 8001)
- Criar, listar, atualizar e encerrar vagas com todos os atributos (título, área, salário, requisitos)
- Consulta filtrada por status (abertas, encerradas, em andamento)
- Histórico completo de alterações

### Gestão de Processos Seletivos (`process-management` · porta 8002)
- Criar processos vinculados a uma vaga com fases customizáveis
- Avançar ou retroceder candidatos entre etapas do funil
- Monitoramento de SLA por processo com alertas automáticos
- Identificação de gargalos na linha do tempo (`process_timeline`)
- Encerrar ou cancelar processos com registro de motivo

### Triagem de Candidatos (`candidate-screening` · porta 8003)
- Cadastrar candidatos com perfil completo (experiência, habilidades, expectativa salarial)
- Avaliar fit do candidato com a vaga e registrar feedback estruturado
- Aprovar ou reprovar com justificativa rastreável

### Agendamento de Entrevistas (`interview-scheduling` · porta 8004)
- Verificar disponibilidade de entrevistadores cadastrados
- Agendar, reagendar e cancelar entrevistas com controle de conflitos
- Listar agenda do entrevistador por período
- Registrar resultado e feedback pós-entrevista

### Interface Conversacional (AgentUI · AgentOS)
- Chat em linguagem natural com streaming de respostas (SSE)
- 7 widgets contextuais renderizados automaticamente na conversa (dashboard de processos, board de candidatos, calendário de entrevistas etc.)
- Histórico de sessão persistido por usuário com autenticação JWT
- RBAC: controle de acesso por papel (recrutador, gestor, admin)

### Integração LiGiaPro (Orchestrator · porta 8000)
- MCP server que expõe o agente como ferramenta plugável ao ecossistema LiGiaPro
- Uma única tool `handle_recruitment_message(message, session_id)` encapsula toda a lógica
- Histórico de conversa por `session_id` (usuário da LiGiaPro) persistido no PostgreSQL
- Acessível via Caddy em `/mcp/recruitment` — compatível com WhatsApp, Teams e Webchat

## Arquitetura

> Diagramas interativos — abra no navegador:
> - **[docs/layers.html](docs/layers.html)** — diagrama de camadas (Frontend → Infra)
> - **[docs/uml-classes.html](docs/uml-classes.html)** — diagrama de classes UML (modelos, atributos, relacionamentos)
> - **[docs/uml-components.html](docs/uml-components.html)** — diagrama de componentes UML (interfaces, dependências, portas)
> - **[docs/architecture.html](docs/architecture.html)** — visão completa com detalhes de todas as camadas

```
 ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
 │  AgentUI  (Next.js :3000)        │   │  LiGiaPro  (externo)             │
 │  Chat · Widgets                  │   │  WhatsApp · Teams · Webchat      │
 └─────────────────┬────────────────┘   └─────────────────┬────────────────┘
                   │  HTTP / SSE                           │  MCP (streamable-http)
 ┌─────────────────▼────────────────┐   ┌─────────────────▼────────────────┐
 │  AgentOS  (FastAPI :7777)        │   │  Orchestrator  (FastMCP :8000)   │
 │  JWT RBAC · WebSocket streaming  │   │  handle_recruitment_message      │
 │  sessões PostgreSQL              │   │  session_id · PostgresDb         │
 └─────────────────┬────────────────┘   └─────────────────┬────────────────┘
                   │  MCPTools (Agno)                      │  make_recruitment_agent(db=…)
                   └──────────────────┬────────────────────┘
                                      │
          ┌───────────────────────────▼──────────────────────────────┐
          │      Recruitment Agent  (Agno + claude-sonnet-4-5)        │
          │  7 widgets · histórico de conversas · instruções PT-BR    │
          └──────┬──────────────┬─────────────────┬──────────────┬───┘
                 │              │   MCP Protocol (streamable-http)
          ┌──────▼───┐   ┌──────▼──────┐   ┌──────▼──────┐   ┌──▼──────────┐
          │:8001      │   │:8002        │   │:8003        │   │:8004        │
          │job-       │   │process-     │   │candidate-   │   │interview-   │
          │opening    │   │management   │   │screening    │   │scheduling   │
          │5 tools    │   │8 tools      │   │4 tools      │   │7 tools      │
          └──────┬────┘   └──────┬──────┘   └──────┬──────┘   └──┬──────────┘
                 └───────────────┴──────────────────┴─────────────┘
                                      │  chamadas async
          ┌───────────────────────────▼──────────────────────────────┐
          │      Services + Schemas  (services/ · schemas/)           │
          │  Lógica de negócio pura · Pydantic v2 · SLA · gargalos   │
          └───────────────────────────┬──────────────────────────────┘
                                      │  repository pattern
          ┌───────────────────────────▼──────────────────────────────┐
          │      SQLAlchemy 2 + Repositories  (db/)                   │
          │  AsyncSession · asyncpg · pool_size=5 · Alembic           │
          └───────────────────────────┬──────────────────────────────┘
                                      │  postgresql+asyncpg://
          ┌───────────────────────────▼──────────────────────────────┐
          │      PostgreSQL 16  (Docker :5432)                        │
          │  job_openings · selection_processes · candidates          │
          │  interviews · interviewers · process_timeline             │
          └──────────────────────────────────────────────────────────┘
```

| Camada | Tecnologia | Porta |
|---|---|---|
| Frontend | Next.js 15 + React 18 + Zustand | :3000 |
| API Gateway | FastAPI (AgentOS) + JWT RBAC | :7777 |
| Integração LiGiaPro | FastMCP 2.0 (Orchestrator) | :8000 |
| Agente IA | Agno + Claude Sonnet 4.5 | — |
| Protocolo | MCP via FastMCP 2.0 (streamable-http) | — |
| MCP Servers | 4 instâncias de domínio | :8001–:8004 |
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
| `ORCHESTRATOR_SERVER_URL` | URL do MCP server orquestrador (para LiGiaPro) |
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
| Orchestrator MCP (LiGiaPro) | `http://localhost:8000/mcp` |
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

## Integração com a LiGiaPro

O agente de recrutamento expõe um **MCP server** dedicado (Orchestrator) que a LiGiaPro consome como qualquer outro agente especializado do ecossistema — via protocolo MCP (streamable-http).

### Endpoint MCP

| Ambiente | URL |
|---|---|
| Local (dev) | `http://localhost:8000/mcp` |
| Via Caddy (produção) | `https://<domínio>/mcp/recruitment` |

### Tool disponível

O Orchestrator expõe **uma única tool** que encapsula toda a lógica de recrutamento:

```
handle_recruitment_message(message: str, session_id: str) → str
```

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `message` | `str` | Mensagem do usuário em linguagem natural (PT-BR) |
| `session_id` | `str` | Identificador único da sessão — use o `user_id` ou `conversation_id` da LiGiaPro |

A resposta é uma `str` em markdown que pode incluir blocos JSON de widget com prefixo `__widget` para renderização de dashboards, boards de candidatos, calendários de entrevistas etc. Se a LiGiaPro não renderizar widgets, o texto markdown já é autocontido e legível.

### Como registrar o agente na LiGiaPro

A LiGiaPro descobre as capacidades do agente via MCP — basta apontar para o endpoint:

```json
{
  "name": "recruitment-orchestrator",
  "transport": "streamable-http",
  "url": "https://<domínio>/mcp/recruitment"
}
```

O protocolo MCP expõe automaticamente o schema da tool `handle_recruitment_message` com seus parâmetros e docstring. O orquestrador LiGiaPro (padrão Magentic) identifica essa tool e a aciona quando o usuário fizer perguntas relacionadas a vagas, processos seletivos, candidatos ou entrevistas.

### Gerenciamento de sessão e histórico

O Orchestrator mantém **histórico de conversa por `session_id`** em uma tabela PostgreSQL dedicada (`orchestrator_sessions`) — separada do histórico do AgentUI. Isso garante que cada usuário da LiGiaPro tenha continuidade de contexto entre mensagens distintas, mesmo que a conversa seja retomada horas depois.

```
Usuário LiGiaPro
      │
      │  MCP call: handle_recruitment_message(
      │      message="Quais vagas estão abertas?",
      │      session_id="ligia_user_42"
      │  )
      ▼
Orchestrator (:8000)
      │  Recupera histórico de session "ligia_user_42"
      │  Envia ao Recruitment Agent
      ▼
Recruitment Agent (Agno + Claude)
      │  Consulta MCP servers internos (:8001–:8004)
      │  Gera resposta em PT-BR
      ▼
Orchestrator
      │  Persiste histórico atualizado
      │  Retorna resposta em markdown
      ▼
LiGiaPro → Usuário (WhatsApp / Teams / Webchat)
```

### Exemplo de chamada MCP (Python)

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("https://<domínio>/mcp/recruitment") as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(
            "handle_recruitment_message",
            {"message": "Abra uma vaga de Engenheiro Backend Sênior", "session_id": "user_42"},
        )
        print(result.content[0].text)
```

## Estrutura do projeto

```
ia-recruitment/
├── agentos.py                      # Entrypoint da API de produção (AgentOS)
├── agents/
│   └── recruitment_agent.py        # Factory make_recruitment_agent() + singleton AgentOS
├── tools/                          # FastMCP servers
│   ├── recruitment_orchestrator_server.py  # Gateway MCP para a LiGiaPro (:8000)
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
