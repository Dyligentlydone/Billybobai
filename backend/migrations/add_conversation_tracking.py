"""
Migration to add conversation tracking fields to messages table
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_conversation_tracking'
down_revision = None  # Set this to the previous migration or None if this is the first one

def upgrade():
    """Add conversation tracking fields to messages table"""
    # Add conversation_id column
    op.add_column('messages', 
        sa.Column('conversation_id', sa.String(36), nullable=True)
    )
    
    # Add index on conversation_id for faster lookups
    op.create_index('ix_messages_conversation_id', 'messages', ['conversation_id'])
    
    # Add is_first_in_conversation column
    op.add_column('messages',
        sa.Column('is_first_in_conversation', sa.Boolean(), server_default='false', nullable=False)
    )
    
    # Add response_to_message_id column with foreign key reference
    op.add_column('messages',
        sa.Column('response_to_message_id', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint for response_to_message_id
    op.create_foreign_key(
        'fk_response_to_message', 'messages', 'messages',
        ['response_to_message_id'], ['id']
    )

def downgrade():
    """Remove conversation tracking fields from messages table"""
    # Remove foreign key constraint
    op.drop_constraint('fk_response_to_message', 'messages', type_='foreignkey')
    
    # Remove columns in reverse order
    op.drop_column('messages', 'response_to_message_id')
    op.drop_column('messages', 'is_first_in_conversation')
    op.drop_index('ix_messages_conversation_id', table_name='messages')
    op.drop_column('messages', 'conversation_id')
