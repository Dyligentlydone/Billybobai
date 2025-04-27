"""Add client_passcodes table

Revision ID: add_client_passcodes_table
Revises: c463f9fa3dd9
Create Date: 2025-04-27 10:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import json

# revision identifiers, used by Alembic.
revision = 'add_client_passcodes_table'
down_revision = 'c463f9fa3dd9'  # Set this to the latest migration you have
branch_labels = None
depends_on = None


def upgrade():
    # Create client_passcodes table
    op.create_table('client_passcodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.String(length=255), nullable=False),
        sa.Column('passcode', sa.String(length=5), nullable=False),
        sa.Column('permissions', sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop client_passcodes table
    op.drop_table('client_passcodes')
