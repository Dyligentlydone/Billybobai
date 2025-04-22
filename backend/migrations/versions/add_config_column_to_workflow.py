"""
Add config column to Workflow model
"""
from alembic import op
import sqlalchemy as sa

# Add these required variables for Alembic
revision = 'add_config_column_to_workflow'
down_revision = None  # This is the first migration
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('workflows', sa.Column('config', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('workflows', 'config')
