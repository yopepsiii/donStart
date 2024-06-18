"""id to guid in creator/user_id

Revision ID: c6a7aa80e076
Revises: 0039e8fe894f
Create Date: 2024-06-17 19:22:39.501409

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6a7aa80e076'
down_revision: Union[str, None] = '0039e8fe894f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Games', sa.Column('creator_guid', sa.Uuid(), nullable=False))
    op.drop_constraint('Games_creator_id_fkey', 'Games', type_='foreignkey')
    op.create_foreign_key(None, 'Games', 'Users', ['creator_guid'], ['guid'], ondelete='CASCADE')
    op.drop_column('Games', 'creator_id')
    op.add_column('Roles', sa.Column('user_guid', sa.Uuid(), nullable=False))
    op.drop_constraint('Roles_user_id_fkey', 'Roles', type_='foreignkey')
    op.create_foreign_key(None, 'Roles', 'Users', ['user_guid'], ['guid'], ondelete='CASCADE')
    op.drop_column('Roles', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Roles', sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'Roles', type_='foreignkey')
    op.create_foreign_key('Roles_user_id_fkey', 'Roles', 'Users', ['user_id'], ['guid'], ondelete='CASCADE')
    op.drop_column('Roles', 'user_guid')
    op.add_column('Games', sa.Column('creator_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'Games', type_='foreignkey')
    op.create_foreign_key('Games_creator_id_fkey', 'Games', 'Users', ['creator_id'], ['guid'], ondelete='CASCADE')
    op.drop_column('Games', 'creator_guid')
    # ### end Alembic commands ###
