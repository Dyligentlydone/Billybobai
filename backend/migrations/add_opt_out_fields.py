"""
Migration script to add opt-out tracking fields to the messages table.

This script adds:
1. is_opted_out Boolean column 
2. opted_out_at DateTime column

These allow tracking opt-out status directly with messages.
"""
from sqlalchemy import Boolean, DateTime, Column, MetaData, Table

# Import the database connection
from app.db import db

def upgrade():
    """Add opt-out tracking fields to messages table"""
    
    # Get metadata from engine
    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    
    # Get messages table
    messages = Table('messages', metadata, autoload_with=db.engine)
    
    # Add is_opted_out column if it doesn't exist
    if 'is_opted_out' not in messages.columns:
        db.engine.execute('ALTER TABLE messages ADD COLUMN is_opted_out BOOLEAN DEFAULT FALSE')
    
    # Add opted_out_at column if it doesn't exist
    if 'opted_out_at' not in messages.columns:
        db.engine.execute('ALTER TABLE messages ADD COLUMN opted_out_at DATETIME')
    
    print("Added opt-out tracking fields to messages table")

def downgrade():
    """Remove opt-out tracking fields from messages table"""
    
    # Get metadata from engine
    metadata = MetaData()
    metadata.reflect(bind=db.engine)
    
    # Get messages table
    messages = Table('messages', metadata, autoload_with=db.engine)
    
    # Remove columns if they exist
    if 'is_opted_out' in messages.columns:
        db.engine.execute('ALTER TABLE messages DROP COLUMN is_opted_out')
    
    if 'opted_out_at' in messages.columns:
        db.engine.execute('ALTER TABLE messages DROP COLUMN opted_out_at')
    
    print("Removed opt-out tracking fields from messages table")

if __name__ == "__main__":
    upgrade()
