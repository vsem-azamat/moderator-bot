"""Add additional columns for metadata (created_at, modified_at,*names/titles) for User,Chat tables

Revision ID: 97c024e13e5c
Revises: 7d4b7f6991af
Create Date: 2024-12-05 16:58:03.529837

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "97c024e13e5c"
down_revision: Union[str, None] = "7d4b7f6991af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("chats", sa.Column("title", sa.String(), nullable=True))
    op.add_column("chats", sa.Column("is_forum", sa.Boolean(), nullable=True))
    op.add_column("chats", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("chats", sa.Column("modified_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("username", sa.String(), nullable=True))
    op.add_column("users", sa.Column("first_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("last_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("modified_at", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "modified_at")
    op.drop_column("users", "created_at")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
    op.drop_column("users", "username")
    op.drop_column("chats", "modified_at")
    op.drop_column("chats", "created_at")
    op.drop_column("chats", "is_forum")
    op.drop_column("chats", "title")
    # ### end Alembic commands ###
