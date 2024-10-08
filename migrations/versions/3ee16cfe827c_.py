"""empty message

Revision ID: 3ee16cfe827c
Revises: 
Create Date: 2024-09-06 06:45:44.042037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ee16cfe827c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teerequests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Monday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('Tuesday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('Wednesday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('Thursday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('Friday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('Saturday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        batch_op.add_column(sa.Column('Sunday_guest', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('teerequests', schema=None) as batch_op:
        batch_op.drop_column('Sunday_guest')
        batch_op.drop_column('Saturday_guest')
        batch_op.drop_column('Friday_guest')
        batch_op.drop_column('Thursday_guest')
        batch_op.drop_column('Wednesday_guest')
        batch_op.drop_column('Tuesday_guest')
        batch_op.drop_column('Monday_guest')

    # ### end Alembic commands ###
