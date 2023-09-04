"""initial

Revision ID: 481c92d46742
Revises: 
Create Date: 2023-09-04 14:26:45.837453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '481c92d46742'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.String(length=64), nullable=True),
    sa.Column('last_name', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('user_id', name='user_pk')
    )
    op.create_table('categories',
    sa.Column('category_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('category_name', sa.String(length=20), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.CheckConstraint('Length(category_name) > 0'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('category_id'),
    sa.UniqueConstraint('user_id', 'category_name')
    )
    op.create_table('actions',
    sa.Column('action_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('action_name', sa.String(length=20), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.CheckConstraint('Length(action_name) > 0'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.category_id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('action_id'),
    sa.UniqueConstraint('action_name', 'category_id', 'user_id')
    )
    op.create_table('trackers',
    sa.Column('tracker_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('duration', sa.Interval(), nullable=True),
    sa.Column('track_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('track_end', sa.DateTime(timezone=True), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('action_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['action_id'], ['actions.action_id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['category_id'], ['categories.category_id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('tracker_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('trackers')
    op.drop_table('actions')
    op.drop_table('categories')
    op.drop_table('users')
    # ### end Alembic commands ###
