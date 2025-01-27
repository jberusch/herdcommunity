"""made yelp_link longer

Revision ID: 3ef2e3c6f98c
Revises: a97509e996f7
Create Date: 2019-12-24 18:42:09.625813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ef2e3c6f98c'
down_revision = 'a97509e996f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('associations', 'num_vists')
    op.drop_index('ix_destinations_name', table_name='destinations')
    op.create_index(op.f('ix_destinations_name'), 'destinations', ['name'], unique=True)
    op.drop_column('destinations', 'address')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('destinations', sa.Column('address', sa.VARCHAR(length=200), nullable=True))
    op.drop_index(op.f('ix_destinations_name'), table_name='destinations')
    op.create_index('ix_destinations_name', 'destinations', ['name'], unique=False)
    op.add_column('associations', sa.Column('num_vists', sa.INTEGER(), nullable=True))
    # ### end Alembic commands ###
