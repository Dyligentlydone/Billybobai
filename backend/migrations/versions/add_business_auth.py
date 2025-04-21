"""add business auth

Revision ID: add_business_auth
Revises: 
Create Date: 2025-04-17 21:59:54.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_business_auth'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to businesses table
    with op.batch_alter_table('businesses') as batch_op:
        batch_op.add_column(sa.Column('passcode_hash', sa.String(255), nullable=True))
        batch_op.add_column(sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('visible_metrics', sqlite.JSON, nullable=True))

def downgrade():
    # Remove new columns from businesses table
    with op.batch_alter_table('businesses') as batch_op:
        batch_op.drop_column('passcode_hash')
        batch_op.drop_column('is_admin')
        batch_op.drop_column('visible_metrics')
