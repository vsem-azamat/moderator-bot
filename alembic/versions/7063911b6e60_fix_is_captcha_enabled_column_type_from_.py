"""fix is_captcha_enabled column type from integer to boolean

Revision ID: 7063911b6e60
Revises: 97c024e13e5c
Create Date: 2025-08-15 16:15:31.070211

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7063911b6e60'
down_revision: Union[str, None] = '97c024e13e5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert INTEGER column to BOOLEAN for is_captcha_enabled
    # First, convert existing integer values (0/1) to boolean (false/true)
    op.execute("ALTER TABLE chats ALTER COLUMN is_captcha_enabled TYPE BOOLEAN USING is_captcha_enabled::boolean")


def downgrade() -> None:
    # Convert BOOLEAN back to INTEGER for is_captcha_enabled
    op.execute("ALTER TABLE chats ALTER COLUMN is_captcha_enabled TYPE INTEGER USING CASE WHEN is_captcha_enabled THEN 1 ELSE 0 END")
