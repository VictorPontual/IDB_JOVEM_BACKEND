"""add tipo_evento to evento

Revision ID: c3a9f1e2d7b4
Revises: b7d4e1f9a3c2
Create Date: 2026-06-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3a9f1e2d7b4"
down_revision: Union[str, Sequence[str], None] = "b7d4e1f9a3c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("evento", sa.Column("tipo_evento", sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("evento", "tipo_evento")
