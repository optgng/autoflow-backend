"""add habit date fields: start_date, end_date, end_after_count, interval_start, interval_end

Revision ID: 6c3d8e2f5a1b
Revises: 5b2e7c1d4f8a
Create Date: 2026-03-27 02:42:00.000000+00:00
"""
from typing import Sequence, Union
from alembic import op

revision: str = '6c3d8e2f5a1b'
down_revision: Union[str, None] = '5b2e7c1d4f8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE finances.habits
        ADD COLUMN IF NOT EXISTS start_date        DATE    NULL,
        ADD COLUMN IF NOT EXISTS end_date          DATE    NULL,
        ADD COLUMN IF NOT EXISTS end_after_count   INTEGER NULL,
        ADD COLUMN IF NOT EXISTS interval_start    DATE    NULL,
        ADD COLUMN IF NOT EXISTS interval_end      DATE    NULL;
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE finances.habits
        DROP COLUMN IF EXISTS start_date,
        DROP COLUMN IF EXISTS end_date,
        DROP COLUMN IF EXISTS end_after_count,
        DROP COLUMN IF EXISTS interval_start,
        DROP COLUMN IF EXISTS interval_end;
    """)
