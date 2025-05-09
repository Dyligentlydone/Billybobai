"""
Script to apply database changes for conversation tracking
"""
import os
import logging
from sqlalchemy import create_engine, text
from config.database import DATABASE_URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def apply_sql_changes():
    """Apply SQL changes to add conversation tracking fields"""
    logger.info("Connecting to database...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # SQL statements to execute
    sql_statements = [
        # Add conversation_id column
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS conversation_id VARCHAR(36);",
        
        # Add index on conversation_id 
        "CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);",
        
        # Add is_first_in_conversation column
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS is_first_in_conversation BOOLEAN NOT NULL DEFAULT FALSE;",
        
        # Add response_to_message_id column
        "ALTER TABLE messages ADD COLUMN IF NOT EXISTS response_to_message_id INTEGER;",
        
        # Add foreign key constraint
        """
        ALTER TABLE messages 
        DROP CONSTRAINT IF EXISTS fk_response_to_message;
        
        ALTER TABLE messages 
        ADD CONSTRAINT fk_response_to_message 
        FOREIGN KEY (response_to_message_id) REFERENCES messages(id);
        """
    ]
    
    # Execute each SQL statement
    with engine.connect() as connection:
        for sql in sql_statements:
            try:
                logger.info(f"Executing: {sql[:60]}...")
                connection.execute(text(sql))
                logger.info("Success!")
            except Exception as e:
                logger.error(f"Error executing SQL: {str(e)}")
                # Continue with other statements even if one fails
    
    logger.info("Database changes applied.")

if __name__ == "__main__":
    apply_sql_changes()
