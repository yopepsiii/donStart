"""empty message

Revision ID: 1d66899844c0
Revises: 66213098d61e
Create Date: 2024-07-05 11:30:42.933258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d66899844c0'
down_revision: Union[str, None] = '66213098d61e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
