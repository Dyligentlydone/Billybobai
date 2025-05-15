"""
Script to run the migration to add conversation tracking fields
"""
import os
import sys
from alembic import command
from alembic.config import Config

# Set up Alembic configuration
alembic_cfg = Config("alembic.ini")

def run_migration(migration_script):
    """Run the specified migration script"""
    print(f"Running migration: {migration_script}")
    
    # Get the full path to the migration script
    script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")
    script_path = os.path.join(script_dir, migration_script)
    
    if not os.path.exists(script_path):
        print(f"Error: Migration script {script_path} not found")
        return False
    
    try:
        # Create a revision based on the script
        command.revision(alembic_cfg, 
                        message=f"Apply {migration_script}", 
                        autogenerate=False,
                        rev_id=f"{os.path.splitext(migration_script)[0]}")
        
        # Run the upgrade to latest
        command.upgrade(alembic_cfg, "head")
        
        print("Migration completed successfully")
        return True
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

if __name__ == "__main__":
    # If no script specified, use default
    migration_script = sys.argv[1] if len(sys.argv) > 1 else "add_conversation_tracking.py"
    run_migration(migration_script)
