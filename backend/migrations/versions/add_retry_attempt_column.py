"""add retry attempt column

Revision ID: add_retry_attempt_column
Revises: add_opt_outs_table
Create Date: 2025-04-16 11:03:58.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_retry_attempt_column'
down_revision = 'add_opt_outs_table'  # Update this to your last migration's revision ID
branch_labels = None
depends_on = None

def upgrade():
    # Add retry_attempt column to sms_messages
    op.add_column('sms_messages', sa.Column('retry_attempt', sa.Integer(), nullable=True))
    op.add_column('sms_messages', sa.Column('metadata', sa.JSON(), nullable=True))

    # Add index for status and retry_attempt
    op.create_index('idx_sms_status_retry', 'sms_messages', ['status', 'retry_attempt'])

def downgrade():
    op.drop_index('idx_sms_status_retry')
    op.drop_column('sms_messages', 'metadata')
    op.drop_column('sms_messages', 'retry_attempt')
