"""merge collation fix and auto_delete_join_leave

Revision ID: 08a895a93f06
Revises: 73a429eaabbb, a1b2c3d4e5f6
Create Date: 2025-08-20 16:50:23.189305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '08a895a93f06'
down_revision: Union[str, None] = ('73a429eaabbb', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
