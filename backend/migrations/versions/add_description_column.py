"""Add description column to businesses table

Revision ID: add_description_column
Revises: 
Create Date: 2025-04-22 16:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_description_column'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add description column to businesses table
    op.add_column('businesses', sa.Column('description', sa.String(1000), nullable=True))


def downgrade():
    # Remove description column from businesses table
    op.drop_column('businesses', 'description')
