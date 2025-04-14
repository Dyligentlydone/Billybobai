import os
from sqlalchemy import create_engine, text

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/twilio_automation')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# SQL statements to create enum types
enum_statements = [
    """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'customersentiment') THEN
            CREATE TYPE customersentiment AS ENUM ('POSITIVE', 'NEUTRAL', 'NEGATIVE');
        END IF;
    END $$;
    """,
    """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'metrictype') THEN
            CREATE TYPE metrictype AS ENUM ('RESPONSE_TIME', 'ERROR_RATE', 'MESSAGE_VOLUME', 'AI_CONFIDENCE', 'CUSTOMER_SENTIMENT');
        END IF;
    END $$;
    """,
    """
    DO $$ 
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'workflowtype') THEN
            CREATE TYPE workflowtype AS ENUM ('SMS', 'EMAIL', 'VOICE');
        END IF;
    END $$;
    """
]

def create_enums():
    """Create enum types if they don't exist."""
    with engine.connect() as conn:
        for statement in enum_statements:
            conn.execute(text(statement))
            conn.commit()

if __name__ == '__main__':
    create_enums()
