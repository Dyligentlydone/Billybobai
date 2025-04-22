"""add opt outs table

Revision ID: add_opt_outs_table
Revises: previous_revision
Create Date: 2025-04-16 10:59:22.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_opt_outs_table'
down_revision = None  # Update this to your last migration's revision ID
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('opt_outs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=15), nullable=False),
        sa.Column('business_id', sa.String(length=255), nullable=False),  # Changed from Integer to String to match businesses.id
        sa.Column('opted_out_at', sa.DateTime(), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('phone_number', 'business_id', name='uq_opt_out_phone_business'),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
    )
    
    # Add opt_out status to sms_messages table
    op.add_column('sms_messages', sa.Column('is_opted_out', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('sms_messages', 'is_opted_out')
    op.drop_table('opt_outs')
