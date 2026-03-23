.PHONY: install install-dev start stop restart test lint format check fix status help \
        db-up db-down db-logs db-shell migrate migrate-auto migrate-history

# ─── Configuração ────────────────────────────────────────────────────────────

PYTHON  := uv run python
PYTEST  := uv run pytest
RUFF    := uv run ruff

# ─── Ambiente ────────────────────────────────────────────────────────────────

install:
	uv sync

install-dev:
	uv sync --extra dev

# ─── Banco de dados (Docker) ─────────────────────────────────────────────────

db-up:
	docker compose up -d
	@echo "Aguardando PostgreSQL ficar pronto..."
	@until docker compose exec postgres pg_isready -U recruitment_user -d recruitment > /dev/null 2>&1; do sleep 1; done
	@echo "PostgreSQL pronto em localhost:5432"
	@echo "pgAdmin disponível em http://localhost:5050 (admin@recruitment.local / admin)"

db-down:
	docker compose down

db-stop:
	docker compose stop

db-logs:
	docker compose logs -f postgres

db-shell:
	docker compose exec postgres psql -U recruitment_user -d recruitment

db-reset:
	docker compose down -v
	docker compose up -d

# ─── Migrações (Alembic) ─────────────────────────────────────────────────────

migrate:
	uv run alembic upgrade head

migrate-auto:
	@read -p "Descrição da migration: " msg; \
	uv run alembic revision --autogenerate -m "$$msg"

migrate-history:
	uv run alembic history --verbose

migrate-rollback:
	uv run alembic downgrade -1

seed:
	uv run python scripts/seed.py

# ─── Servidores ──────────────────────────────────────────────────────────────

start:
	@./start.sh

stop:
	@echo "Encerrando todos os serviços..."
	@pkill -f "fastmcp run" 2>/dev/null || true
	@pkill -f "agentos.py"  2>/dev/null || true
	@sleep 1
	@echo "Pronto."

restart: stop
	@sleep 1
	@./start.sh

# ─── Testes ──────────────────────────────────────────────────────────────────

test:
	$(PYTEST)

test-verbose:
	$(PYTEST) -v

test-services:
	$(PYTEST) tests/services/

test-tools:
	$(PYTEST) tests/tools/

test-cov:
	$(PYTEST) --cov=. --cov-report=term-missing

# ─── Qualidade de código ─────────────────────────────────────────────────────

lint:
	$(RUFF) check .

format:
	$(RUFF) format .

check: lint
	$(RUFF) check . --select I
	@echo "OK"

fix:
	$(RUFF) check . --fix
	$(RUFF) format .

# ─── Utilitários ─────────────────────────────────────────────────────────────

status:
	@echo "Portas em uso:"
	@ss -tlnp 2>/dev/null | grep -E "7777|800[1-4]|5432|5050" || echo "  Nenhum serviço detectado"

help:
	@echo ""
	@echo "Comandos disponíveis:"
	@echo ""
	@echo "  Ambiente"
	@echo "    make install           Instala dependências de produção"
	@echo "    make install-dev       Instala dependências + dev (pytest, ruff)"
	@echo ""
	@echo "  Banco de dados"
	@echo "    make db-up             Sobe PostgreSQL + pgAdmin via Docker"
	@echo "    make db-down           Para e remove os containers"
	@echo "    make db-stop           Para os containers (mantém volumes)"
	@echo "    make db-logs           Logs do PostgreSQL em tempo real"
	@echo "    make db-shell          Abre psql no container"
	@echo "    make db-reset          Remove volumes e recria do zero"
	@echo ""
	@echo "  Migrações"
	@echo "    make migrate           Aplica todas as migrations pendentes"
	@echo "    make migrate-auto      Gera nova migration pelo autogenerate"
	@echo "    make migrate-history   Exibe histórico de migrations"
	@echo "    make migrate-rollback  Reverte a última migration"
	@echo "    make seed              Popula o banco com dados fictícios"
	@echo ""
	@echo "  Servidores"
	@echo "    make start             Sobe MCP servers (8001-8004) + AgentOS (7777)"
	@echo "    make stop              Encerra todos os serviços"
	@echo "    make restart           stop + start"
	@echo "    make status            Mostra portas em uso"
	@echo ""
	@echo "  Testes"
	@echo "    make test              Roda todos os testes"
	@echo "    make test-verbose      Testes com output detalhado"
	@echo "    make test-services     Apenas testes de services/"
	@echo "    make test-tools        Apenas testes de tools/"
	@echo "    make test-cov          Testes com relatório de cobertura"
	@echo ""
	@echo "  Qualidade"
	@echo "    make lint              Verifica problemas com ruff"
	@echo "    make format            Formata código com ruff"
	@echo "    make fix               lint + format automático"
	@echo "    make check             Lint + verificação de imports"
	@echo ""
