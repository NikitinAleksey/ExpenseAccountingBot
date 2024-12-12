"""Add month limits

Revision ID: 54413cc9dd16
Revises: c229574018c1
Create Date: 2024-12-06 10:44:27.395551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54413cc9dd16'
down_revision: Union[str, None] = 'c229574018c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('monthly_limits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('alcohol', sa.Integer(), nullable=True),
    sa.Column('charity', sa.Integer(), nullable=True),
    sa.Column('debts', sa.Integer(), nullable=True),
    sa.Column('household', sa.Integer(), nullable=True),
    sa.Column('eating_out', sa.Integer(), nullable=True),
    sa.Column('health', sa.Integer(), nullable=True),
    sa.Column('cosmetics_and_care', sa.Integer(), nullable=True),
    sa.Column('education', sa.Integer(), nullable=True),
    sa.Column('pets', sa.Integer(), nullable=True),
    sa.Column('purchases', sa.Integer(), nullable=True),
    sa.Column('products', sa.Integer(), nullable=True),
    sa.Column('travel', sa.Integer(), nullable=True),
    sa.Column('entertainment', sa.Integer(), nullable=True),
    sa.Column('friends_and_family', sa.Integer(), nullable=True),
    sa.Column('cigarettes', sa.Integer(), nullable=True),
    sa.Column('sport', sa.Integer(), nullable=True),
    sa.Column('devices', sa.Integer(), nullable=True),
    sa.Column('transport', sa.Integer(), nullable=True),
    sa.Column('services', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.tg_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', name='uq_user_monthly_limits')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('monthly_limits')
    # ### end Alembic commands ###
