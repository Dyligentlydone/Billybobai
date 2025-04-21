"""
Add config column to Workflow model
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('workflows', sa.Column('config', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('workflows', 'config')
