from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ee01add_client_passcodes'
down_revision = '00aba09dab33'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'client_passcodes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('business_id', sa.Integer, sa.ForeignKey('businesses.id'), nullable=False),
        sa.Column('passcode', sa.String(5), nullable=False),
        sa.Column('permissions', sa.JSON, nullable=False)
    )


def downgrade():
    op.drop_table('client_passcodes')
