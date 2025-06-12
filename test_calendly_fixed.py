#!/usr/bin/env python3
"""
Test script to verify the fixed Calendly API integration
This script tests both the get_event_types and get_available_slots methods
"""
import os
import sys
import asyncio
import httpx
import logging
from datetime import datetime, timedelta
from pprint import pprint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the backend directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the necessary modules
try:
    from app.schemas.calendly import CalendlyConfig
    from app.services.calendly import CalendlyService
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error("Make sure you're running this script from the project root directory")
    sys.exit(1)

async def test_calendly_integration():
    """Test the Calendly API integration with the fixed methods"""
    # Get the token from environment variable or ask for it
    token = os.environ.get('CALENDLY_TOKEN')
    if not token:
        token = input("Enter your Calendly token: ")
        if not token:
            logger.error("No token provided")
            return
    
    # Get the user URI from environment variable or ask for it
    user_uri = os.environ.get('CALENDLY_USER_URI')
    if not user_uri:
        user_uri = input("Enter your Calendly user URI (or leave blank to auto-fetch): ")
    
    # Create the config
    config = CalendlyConfig(
        access_token=token,
        user_uri=user_uri,
        booking_window_days=14
    )
    
    # Create the service
    service = CalendlyService(config)
    
    # Test initialization and user URI fetching
    logger.info("=== Testing initialization and user URI fetching ===")
    try:
        if not user_uri:
            user_uri = await service.initialize()
            logger.info(f"Successfully fetched user URI: {user_uri}")
        else:
            logger.info(f"Using provided user URI: {user_uri}")
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        return
    
    # Test get_event_types
    logger.info("\n=== Testing get_event_types method ===")
    try:
        event_types = await service.get_event_types()
        logger.info(f"Successfully fetched {len(event_types)} event types")
        for i, et in enumerate(event_types):
            logger.info(f"Event Type {i+1}: {et.name} (ID: {et.id})")
        
        # Save the first event type ID for the next test
        if event_types:
            first_event_type_id = event_types[0].id
        else:
            logger.warning("No event types found, cannot test get_available_slots")
            return
    except Exception as e:
        logger.error(f"Failed to get event types: {str(e)}")
        return
    
    # Test get_available_slots
    logger.info("\n=== Testing get_available_slots method ===")
    try:
        # Get slots for the next 14 days
        start_time = datetime.now()
        slots = await service.get_available_slots(
            event_type_id=first_event_type_id,
            start_time=start_time,
            days=14
        )
        
        logger.info(f"Successfully fetched {len(slots)} available slots")
        
        # Display the first 5 slots
        for i, slot in enumerate(slots[:5]):
            slot_time = slot.start_time
            if slot_time.tzinfo:
                slot_time = slot_time.astimezone()  # Convert to local timezone
            logger.info(f"Slot {i+1}: {slot_time.strftime('%a, %b %d at %I:%M %p')}")
        
        if len(slots) > 5:
            logger.info(f"... and {len(slots) - 5} more slots")
    except Exception as e:
        logger.error(f"Failed to get available slots: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_calendly_integration())
