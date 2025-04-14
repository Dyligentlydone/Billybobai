"""
Test script for database models.
"""
import os
import sys
from datetime import datetime

# Add backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.database import DATABASE_URL
from models import (
    Base, Business, User,
    Integration, CalendlyIntegration, TwilioIntegration,
    SendGridIntegration, OpenAIIntegration
)
from models.schemas.integration import IntegrationStatus

def test_models():
    """Test the database models."""
    print(f"Using database: {DATABASE_URL}")
    
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create a test business
        business = Business(
            id="test_business_1",
            name="Test Business",
            domain="testbusiness.com",
            status="active",
            config={
                "name": "Test Business",
                "brand_voice": {
                    "voiceType": "professional",
                    "greetings": ["Hello", "Hi there"],
                    "wordsToAvoid": ["bad", "terrible"]
                }
            }
        )
        session.add(business)
        session.commit()
        print("✅ Created business successfully")

        # Create a test user
        user = User(
            email="test@testbusiness.com",
            password_hash="hashed_password",
            business_id=business.id
        )
        session.add(user)
        session.commit()
        print("✅ Created user successfully")

        # Test Calendly Integration
        calendly = CalendlyIntegration(
            name="Calendly Integration",
            business_id=business.id,
            config={
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "organization_url": "https://calendly.com/testorg"
            }
        )
        assert calendly.validate_config() == True
        session.add(calendly)
        session.commit()
        print("✅ Created Calendly integration successfully")

        # Test Twilio Integration
        twilio = TwilioIntegration(
            name="Twilio Integration",
            business_id=business.id,
            config={
                "account_sid": "test_sid",
                "auth_token": "test_token",
                "phone_number": "+1234567890",
                "messaging_service_sid": "test_messaging_sid"
            }
        )
        assert twilio.validate_config() == True
        assert twilio.get_messaging_service() == "test_messaging_sid"
        session.add(twilio)
        session.commit()
        print("✅ Created Twilio integration successfully")

        # Test SendGrid Integration
        sendgrid = SendGridIntegration(
            name="SendGrid Integration",
            business_id=business.id,
            config={
                "api_key": "test_api_key",
                "from_email": "noreply@testbusiness.com",
                "template_ids": {
                    "welcome": "template_123",
                    "reset": "template_456"
                }
            }
        )
        assert sendgrid.validate_config() == True
        assert sendgrid.get_template_id("welcome") == "template_123"
        session.add(sendgrid)
        session.commit()
        print("✅ Created SendGrid integration successfully")

        # Test OpenAI Integration
        openai = OpenAIIntegration(
            name="OpenAI Integration",
            business_id=business.id,
            config={
                "api_key": "test_api_key",
                "model": "gpt-4",
                "max_tokens": 2000,
                "temperature": 0.7
            }
        )
        assert openai.validate_config() == True
        settings = openai.get_model_settings()
        assert settings["model"] == "gpt-4"
        assert settings["max_tokens"] == 2000
        session.add(openai)
        session.commit()
        print("✅ Created OpenAI integration successfully")

        # Test relationships
        business = session.query(Business).first()
        assert len(business.integrations) == 4
        print("✅ Business has correct number of integrations")

        # Test integration status updates
        calendly.status = IntegrationStatus.ACTIVE
        session.commit()
        assert calendly.status == IntegrationStatus.ACTIVE
        print("✅ Integration status updates work")

        # Test polymorphic queries
        integrations = session.query(Integration).all()
        assert len(integrations) == 4
        integration_types = set(type(i) for i in integrations)
        assert len(integration_types) == 4
        print("✅ Polymorphic queries work correctly")

        print("\n🎉 All tests passed successfully!")

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        raise

    finally:
        # Clean up test data
        session.query(Integration).delete()
        session.query(User).delete()
        session.query(Business).delete()
        session.commit()
        session.close()

if __name__ == "__main__":
    test_models()
