import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from config.database import engine
from models.user import User
from models.api_integration import APIIntegration
from datetime import datetime

def test_database_setup():
    try:
        # Create a new session
        with Session(engine) as session:
            # Create a test user
            test_user = User(
                email="test@example.com",
                password_hash="test_hash_not_for_production"
            )
            session.add(test_user)
            session.flush()  # This will assign an ID to test_user
            
            # Create a test API integration
            test_integration = APIIntegration(
                user_id=test_user.id,
                service_name="twilio",
                credentials={"test": "credentials"},
                is_active=True
            )
            session.add(test_integration)
            
            # Commit the changes
            session.commit()
            
            # Read back the data
            user = session.query(User).filter_by(email="test@example.com").first()
            integration = session.query(APIIntegration).filter_by(user_id=user.id).first()
            
            print("\n=== Database Verification Results ===")
            print(f"User created successfully: {user.email}")
            print(f"API Integration created successfully: {integration.service_name}")
            print("All database operations completed successfully!")
            
            # Cleanup
            session.delete(integration)
            session.delete(user)
            session.commit()
            print("Test data cleaned up successfully!")
            
    except Exception as e:
        print(f"Error during database verification: {str(e)}")
        raise

if __name__ == "__main__":
    test_database_setup()
