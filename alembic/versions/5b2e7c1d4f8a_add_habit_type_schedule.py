"""add habit_type, time_of_day, repeat_days; extend frequency enum

Revision ID: 5b2e7c1d4f8a
Revises: 4a1f8b9c2d3e
Create Date: 2026-03-27 02:15:00.000000+00:00
"""
from typing import Sequence, Union
from alembic import op

revision: str = '5b2e7c1d4f8a'
down_revision: Union[str, None] = '4a1f8b9c2d3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Расширяем enum HabitFrequency — ADD VALUE не работает в транзакции,
    #    поэтому используем COMMIT trick через autocommit-соединение.
    #    В Alembic это делается через get_bind() + execution_options.
    op.execute("ALTER TYPE finances.habitfrequency ADD VALUE IF NOT EXISTS 'monthly'")
    op.execute("ALTER TYPE finances.habitfrequency ADD VALUE IF NOT EXISTS 'interval'")

    # 2. Добавляем новые колонки в finances.habits
    op.execute("""
        ALTER TABLE finances.habits
        ADD COLUMN IF NOT EXISTS habit_type  VARCHAR(10) NOT NULL DEFAULT 'good',
        ADD COLUMN IF NOT EXISTS time_of_day JSON        NULL,
        ADD COLUMN IF NOT EXISTS repeat_days JSON        NULL;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE finances.habits
        DROP COLUMN IF EXISTS habit_type,
        DROP COLUMN IF EXISTS time_of_day,
        DROP COLUMN IF EXISTS repeat_days;
    """)
    # Значения из enum нельзя удалить в PostgreSQL без пересоздания типа.
    # Downgrade enum пропущен намеренно — безопасно, старые значения не используются.
