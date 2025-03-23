import asyncio
import os
from dotenv import load_dotenv
import sys
import logging

# Add the backend directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openai_client import initialize, generate_response

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_openai_integration():
    """Test the OpenAI integration with a simple message"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        # Initialize the client
        initialize(api_key)
        
        # Test context
        context = {
            "business_name": "Test Company",
            "product": "Widget",
            "common_questions": ["How much does it cost?", "When can I get it?"]
        }
        
        # Test message
        message = "Hi! I'm interested in learning more about your widgets."
        
        logging.info("Sending test message to OpenAI...")
        
        # Generate response
        result = await generate_response(
            message=message,
            context=context,
            tone="friendly",
            model="gpt-3.5-turbo",
            max_tokens=150,
            temperature=0.7
        )
        
        # Log results
        logging.info(f"\nResponse: {result.text}")
        logging.info(f"Tokens used: {result.tokens_used}")
        logging.info(f"Model used: {result.model_used}")
        logging.info(f"Cost: ${result.cost:.4f}")
        logging.info(f"Confidence: {result.confidence}")
        
        return True
        
    except Exception as e:
        logging.error(f"Test failed: {str(e)}")
        return False

def main():
    """Run the async test in the event loop"""
    return asyncio.run(test_openai_integration())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
