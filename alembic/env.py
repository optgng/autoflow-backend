# alembic/env.py
from __future__ import annotations
import asyncio  # ← отсутствует
from logging.config import fileConfig  # ← отсутствует

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy.engine import Connection

from src.config import settings
from src.models.base import Base
from src.models.user import User
from src.models.account import Account
from src.models.category import Category
from src.models.transaction import Transaction
from src.models.budget import Budget
from src.models.telegram_link_token import TelegramLinkToken  # ← добавить после создания модели

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Указываем обе схемы
target_metadata.schema_translate_map = None


def get_url() -> str:
    return settings.DATABASE_URL

MANAGED_SCHEMAS = {"finances", "public"}


def include_object(object, name, type_, reflected, compare_to):
    """
    Говорим Alembic какие объекты включать в миграции.
    Всё что не в MANAGED_SCHEMAS — игнорируем.
    """
    # Для таблиц проверяем схему
    if type_ == "table":
        schema = object.schema if hasattr(object, "schema") else None
        if schema not in MANAGED_SCHEMAS:
            return False  # ← не трогаем bot, public и т.д.

    # Для индексов и остального — берём схему из таблицы
    if type_ in ("index", "unique_constraint", "foreign_key_constraint"):
        table_schema = getattr(object.table, "schema", None)
        if table_schema not in MANAGED_SCHEMAS:
            return False

    return True

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_schemas=True,
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_async_migrations())

run_migrations()

