"""fix collation version mismatch for PostgreSQL 17.6

Revision ID: 73a429eaabbb
Revises: 7063911b6e60
Create Date: 2025-08-18 15:02:26.564605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73a429eaabbb'
down_revision: Union[str, None] = '7063911b6e60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix PostgreSQL collation version mismatch after upgrading to 17.6."""
    # Get the database name from the connection
    connection = op.get_bind()

    # Get the current database name
    result = connection.execute(sa.text("SELECT current_database()"))
    database_name = result.scalar()

    # Execute the REFRESH COLLATION VERSION command for the current database
    # This fixes the warning about collation version mismatch when upgrading PostgreSQL
    connection.execute(sa.text(f"ALTER DATABASE {database_name} REFRESH COLLATION VERSION"))


def downgrade() -> None:
    """No downgrade needed for collation version fix."""
    pass
