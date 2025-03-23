import asyncio
import os
from dotenv import load_dotenv
import sys
import logging

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.sms_processor import SMSProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_sms_integration():
    """Test the SMS automation with a sample message"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Test configuration
        config = {
            'business_name': 'Test Company',
            'tone': 'friendly',
            'common_questions': [
                'What are your hours?',
                'How much do your services cost?',
                'Do you offer refunds?'
            ],
            'product_info': {
                'name': 'Premium Widget',
                'price': '$99.99',
                'features': ['Durable', 'Easy to use', 'Lifetime warranty']
            },
            'ai_model': 'gpt-3.5-turbo',
            'zendesk': {
                'enabled': False
            }
        }
        
        # Initialize SMS processor
        processor = SMSProcessor(
            business_id='test123',
            workflow_id='workflow123',
            workflow_name='Test Workflow',
            config=config
        )
        
        # Test message
        from_number = '+12065550123'  # Test phone number
        message_body = "Hi! I'm interested in learning more about your widgets. What's the price and do they come with a warranty?"
        
        logging.info("Processing test SMS message...")
        
        # Process message with TwiML response
        result = await processor.process_incoming_message(
            from_number=from_number,
            message_body=message_body,
            use_twiml=True  # Use TwiML for testing
        )
        
        # Log results
        if result.success:
            logging.info("\nSuccess!")
            logging.info(f"Response: {result.response}")
            if result.message_sid:
                logging.info(f"Message SID: {result.message_sid}")
            if result.ticket_id:
                logging.info(f"Ticket ID: {result.ticket_id}")
        else:
            logging.error(f"\nError: {result.error}")
        
        return result.success
        
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
        return False

def main():
    """Run the async test in the event loop"""
    return asyncio.run(test_sms_integration())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
