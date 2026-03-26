"""add habit_strength to habits

Revision ID: 4a1f8b9c2d3e
Revises: 3e9329094e83
Create Date: 2026-03-27 02:00:00.000000+00:00
"""
from typing import Sequence, Union
from alembic import op

revision: str = '4a1f8b9c2d3e'
down_revision: Union[str, None] = '3e9329094e83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE finances.habits
        ADD COLUMN IF NOT EXISTS habit_strength FLOAT NOT NULL DEFAULT 0.0;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE finances.habits
        DROP COLUMN IF EXISTS habit_strength;
    """)
