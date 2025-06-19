"""new_migration

Revision ID: af28fdb90489
Revises: 27b9698e66d3
Create Date: 2025-06-19 17:36:31.880812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af28fdb90489'
down_revision: Union[str, None] = '27b9698e66d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'user_email', new_column_name='email')


def downgrade() -> None:
    op.alter_column('users', 'email', new_column_name='user_email')
