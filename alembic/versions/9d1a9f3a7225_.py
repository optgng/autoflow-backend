"""empty message

Revision ID: 9d1a9f3a7225
Revises: 002_enrichment, 4cae4220fc21
Create Date: 2026-03-26 16:47:18.737416+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d1a9f3a7225'
down_revision: Union[str, None] = ('002_enrichment', '4cae4220fc21')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
