"""converting association table to association object

Revision ID: 36108cd05115
Revises: 3a150fb4d7a7
Create Date: 2019-12-22 21:44:56.285403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36108cd05115'
down_revision = '3a150fb4d7a7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('associations',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('destination_id', sa.Integer(), nullable=False),
    sa.Column('num_vists', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['destination_id'], ['destinations.destination_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'destination_id')
    )
    op.drop_table('user_destination_identifier')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_destination_identifier',
    sa.Column('destination_id', sa.INTEGER(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['destination_id'], ['destinations.destination_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], )
    )
    op.drop_table('associations')
    # ### end Alembic commands ###
