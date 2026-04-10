#!/bin/sh
set -e
echo "Rodando migrações..."
uv run alembic upgrade head
echo "Migrações concluídas."
