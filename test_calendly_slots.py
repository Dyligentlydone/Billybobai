#!/usr/bin/env python
"""
Test script for Calendly API v2 integration with Personal Access Tokens.
This script tests the get_available_slots method directly.

Usage:
    python test_calendly_slots.py --token YOUR_PAT --event-type EVENT_TYPE_ID

Example:
    python test_calendly_slots.py --token abc123 --event-type abcdef-1234-5678-90ab-cdef12345678
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("calendly_test")

# Import Calendly service
sys.path.append("./backend")
from app.services.calendly import CalendlyService, CalendlyConfig, TimeSlot

async def test_available_slots(token: str, event_type_id: str, days: int = 7, start_date=None):
    """Test the get_available_slots method with a specific event type ID"""
    try:
        # Initialize Calendly service
        logger.info(f"Initializing Calendly service with token (length: {len(token)})")
        config = CalendlyConfig(access_token=token)
        calendly = CalendlyService(config)
        
        # Initialize service to get user info
        logger.info("Getting user info...")
        await calendly.initialize()
        logger.info(f"User URI: {calendly.config.user_uri}")
        
        # Set start date
        if start_date:
            start_time = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start_time = datetime.now()
        
        # Get available slots
        logger.info(f"Getting available slots for event type {event_type_id} for {days} days")
        slots = await calendly.get_available_slots(event_type_id, start_time, days)
        
        # Process results
        if not slots:
            logger.info(f"No available slots found for the next {days} days")
            return
        
        # Group slots by day
        days_dict = {}
        
        for slot in slots:
            day_key = slot.start_time.strftime("%Y-%m-%d")
            
            if day_key not in days_dict:
                days_dict[day_key] = []
            
            days_dict[day_key].append({
                "start": slot.start_time.strftime("%H:%M"),
                "end": slot.end_time.strftime("%H:%M"),
            })
        
        # Print results
        logger.info(f"Found {len(slots)} available slots across {len(days_dict)} days")
        
        for day, slots_list in days_dict.items():
            day_name = datetime.strptime(day, "%Y-%m-%d").strftime("%A, %b %d")
            logger.info(f"\n{day_name} ({day}):")
            for slot in slots_list:
                logger.info(f"  {slot['start']} - {slot['end']}")
        
    except Exception as e:
        logger.error(f"Error testing available slots: {str(e)}")
        raise

async def main():
    """Main function to run the test"""
    parser = argparse.ArgumentParser(description="Test Calendly API v2 integration")
    parser.add_argument("--token", required=True, help="Calendly Personal Access Token")
    parser.add_argument("--event-type", required=True, help="Calendly Event Type ID")
    parser.add_argument("--days", type=int, default=7, help="Number of days to check")
    parser.add_argument("--start-date", help="Start date in YYYY-MM-DD format (defaults to today)")
    
    args = parser.parse_args()
    
    await test_available_slots(args.token, args.event_type, args.days, args.start_date)

if __name__ == "__main__":
    asyncio.run(main())
