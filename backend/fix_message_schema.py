"""
Script to verify and apply missing columns to the messages table
with enhanced error handling and verification
"""
import os
import sys
import logging
import psycopg2
from psycopg2 import sql

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("db_fix")

# Database connection parameters from config
DATABASE_URL = "postgresql://postgres:PQfalVBeDPVwbHFcnEiIHyNKYjNNjorG@caboose.proxy.rlwy.net:46405/railway"

def check_column_exists(cursor, table_name, column_name):
    """Check if a column exists in a table"""
    query = """
    SELECT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    );
    """
    cursor.execute(query, (table_name, column_name))
    return cursor.fetchone()[0]

def verify_changes(conn):
    """Verify all necessary columns exist in the messages table"""
    with conn.cursor() as cursor:
        # Columns we need to verify
        columns = [
            "conversation_id", 
            "is_first_in_conversation", 
            "response_to_message_id"
        ]
        
        missing = []
        for col in columns:
            exists = check_column_exists(cursor, "messages", col)
            if exists:
                logger.info(f"✓ Column '{col}' exists in messages table")
            else:
                logger.error(f"✗ Column '{col}' DOES NOT exist in messages table")
                missing.append(col)
        
        return missing

def apply_schema_changes(conn, missing_columns):
    """Apply schema changes to add missing columns"""
    with conn.cursor() as cursor:
        for col in missing_columns:
            try:
                if col == "conversation_id":
                    logger.info("Adding conversation_id column...")
                    cursor.execute(
                        "ALTER TABLE messages ADD COLUMN conversation_id VARCHAR(36);"
                    )
                    cursor.execute(
                        "CREATE INDEX IF NOT EXISTS ix_messages_conversation_id ON messages (conversation_id);"
                    )
                
                elif col == "is_first_in_conversation":
                    logger.info("Adding is_first_in_conversation column...")
                    cursor.execute(
                        "ALTER TABLE messages ADD COLUMN is_first_in_conversation BOOLEAN NOT NULL DEFAULT FALSE;"
                    )
                
                elif col == "response_to_message_id":
                    logger.info("Adding response_to_message_id column...")
                    cursor.execute(
                        "ALTER TABLE messages ADD COLUMN response_to_message_id INTEGER;"
                    )
                    # Add foreign key constraint
                    cursor.execute("""
                        ALTER TABLE messages 
                        ADD CONSTRAINT fk_response_to_message 
                        FOREIGN KEY (response_to_message_id) REFERENCES messages(id);
                    """)
                
                logger.info(f"Column '{col}' added successfully.")
                conn.commit()
            except Exception as e:
                logger.error(f"Error adding column '{col}': {str(e)}")
                conn.rollback()
                return False
        
        return True

def dump_table_schema(conn, table_name):
    """Dump the schema of a table for debugging"""
    logger.info(f"Current schema for table '{table_name}':")
    with conn.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type, character_maximum_length, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"  {row[0]}: {row[1]}" + 
                       (f"({row[2]})" if row[2] else "") + 
                       (" NULL" if row[3] == 'YES' else " NOT NULL"))

def main():
    """Main function to fix the database schema"""
    logger.info("Starting database schema fix process")
    logger.info(f"Connecting to database: {DATABASE_URL.split('@')[1]}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        logger.info("Successfully connected to the database")
        
        # Dump current schema
        dump_table_schema(conn, "messages")
        
        # Check which columns are missing
        missing_columns = verify_changes(conn)
        
        if not missing_columns:
            logger.info("All required columns already exist. No changes needed.")
            return
        
        # Apply changes for missing columns
        logger.info(f"Found {len(missing_columns)} missing columns: {', '.join(missing_columns)}")
        success = apply_schema_changes(conn, missing_columns)
        
        if success:
            logger.info("Schema changes applied successfully!")
            # Verify again after changes
            still_missing = verify_changes(conn)
            if still_missing:
                logger.error(f"Failed to add some columns: {', '.join(still_missing)}")
            else:
                logger.info("All columns verified after changes")
        else:
            logger.error("Failed to apply schema changes")
        
        # Close the connection
        conn.close()
        logger.info("Database connection closed")
        
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return

if __name__ == "__main__":
    main()
