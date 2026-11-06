"""historial_conversacion: message_id_externo (US-017 CA-3)

Revision ID: c3a91f5e7b20
Revises: 18a1f7ba4819
Create Date: 2026-11-06 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c3a91f5e7b20'
down_revision: Union[str, Sequence[str], None] = '18a1f7ba4819'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'historial_conversacion',
        sa.Column('message_id_externo', sa.String(length=100), nullable=True),
    )
    op.create_index(
        'uq_historial_message_id_externo',
        'historial_conversacion',
        ['message_id_externo'],
        unique=True,
        postgresql_where=sa.text('message_id_externo IS NOT NULL'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        'uq_historial_message_id_externo',
        table_name='historial_conversacion',
        postgresql_where=sa.text('message_id_externo IS NOT NULL'),
    )
    op.drop_column('historial_conversacion', 'message_id_externo')
