"""
Check the PostgreSQL enum definitions in the database
"""
import psycopg2
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters from config
DATABASE_URL = "postgresql://postgres:PQfalVBeDPVwbHFcnEiIHyNKYjNNjorG@caboose.proxy.rlwy.net:46405/railway"

def check_enums():
    """Check the defined enums in PostgreSQL"""
    try:
        # Connect to the database
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Query to get all enum types and their values
        query = """
        SELECT 
            t.typname AS enum_name,
            e.enumlabel AS enum_value
        FROM 
            pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
        ORDER BY 
            enum_name, e.enumsortorder;
        """
        
        cursor.execute(query)
        enums = cursor.fetchall()
        
        # Print the results
        logger.info("PostgreSQL Enum Definitions:")
        current_enum = None
        
        for enum_name, enum_value in enums:
            if enum_name != current_enum:
                logger.info(f"\n{enum_name}:")
                current_enum = enum_name
            
            logger.info(f"  - '{enum_value}'")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking enums: {str(e)}")

if __name__ == "__main__":
    check_enums()
