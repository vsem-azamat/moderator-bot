"""add auto_delete_join_leave to chats table

Revision ID: a1b2c3d4e5f6
Revises: 7063911b6e60
Create Date: 2025-08-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '7063911b6e60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add auto_delete_join_leave column to chats table with nullable=True first
    op.add_column('chats', sa.Column('auto_delete_join_leave', sa.Boolean(), nullable=True))

    # Update existing rows to have default value
    op.execute("UPDATE chats SET auto_delete_join_leave = false WHERE auto_delete_join_leave IS NULL")

    # Now make it NOT NULL
    op.alter_column('chats', 'auto_delete_join_leave', nullable=False, server_default=sa.text('false'))


def downgrade() -> None:
    # Remove auto_delete_join_leave column from chats table
    op.drop_column('chats', 'auto_delete_join_leave')
