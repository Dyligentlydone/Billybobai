import re
from datetime import datetime, timedelta
import logging
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

def extract_date_time(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract date and time information from natural language text.
    Returns a dictionary with structured date/time information.
    """
    text = text.lower()
    result = {
        "raw_text": text,
        "date_found": False,
        "time_found": False,
        "date_text": None,
        "time_text": None,
        "datetime": None,
        "confidence": 0.0
    }
    
    # Date patterns
    today = datetime.now()
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, 
        "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
    }
    
    # Extract specific days of week
    day_match = re.search(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text)
    if day_match:
        target_weekday = weekdays[day_match.group(1)]
        current_weekday = today.weekday()
        days_ahead = target_weekday - current_weekday
        if days_ahead <= 0:  # Target is today or earlier in the week
            days_ahead += 7  # Move to next week
        target_date = today + timedelta(days=days_ahead)
        result["date_found"] = True
        result["date_text"] = day_match.group(1)
        result["confidence"] += 0.4
    
    # Extract relative dates
    if "today" in text:
        target_date = today
        result["date_found"] = True
        result["date_text"] = "today"
        result["confidence"] += 0.5
    elif "tomorrow" in text:
        target_date = today + timedelta(days=1)
        result["date_found"] = True
        result["date_text"] = "tomorrow"
        result["confidence"] += 0.5
    elif "day after tomorrow" in text:
        target_date = today + timedelta(days=2)
        result["date_found"] = True
        result["date_text"] = "day after tomorrow"
        result["confidence"] += 0.5
    # Handle 'next week' queries
    elif re.search(r'\b(next\s+week)\b', text):
        # Calculate the start of next week (next Monday)
        days_until_next_monday = (7 - today.weekday()) % 7
        if days_until_next_monday == 0:
            days_until_next_monday = 7  # If today is Monday, go to next Monday
        target_date = today + timedelta(days=days_until_next_monday)
        result["date_found"] = True
        result["date_text"] = "next week"
        result["confidence"] += 0.8  # High confidence for this pattern
    
    # Time patterns
    time_match = re.search(r'(?:at|for|@)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        
        # Convert to 24-hour format
        if time_match.group(3).lower() == "pm" and hour < 12:
            hour += 12
        elif time_match.group(3).lower() == "am" and hour == 12:
            hour = 0
            
        result["time_found"] = True
        result["time_text"] = time_match.group(0)
        result["confidence"] += 0.4
    else:
        # Try military time format
        military_match = re.search(r'(?:at|for|@)?\s*(\d{1,2}):?(\d{2})', text)
        if military_match:
            hour = int(military_match.group(1))
            minute = int(military_match.group(2))
            if 0 <= hour < 24 and 0 <= minute < 60:
                result["time_found"] = True
                result["time_text"] = military_match.group(0)
                result["confidence"] += 0.3
    
    # Combine date and time if both found
    if result["date_found"] and result["time_found"]:
        # Use the extracted target_date and time info
        if "target_date" in locals() and "hour" in locals() and "minute" in locals():
            result["datetime"] = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            result["confidence"] += 0.2
    elif result["date_found"] and not result["time_found"]:
        # Use noon as default time
        if "target_date" in locals():
            result["datetime"] = target_date.replace(hour=12, minute=0, second=0, microsecond=0)
            result["confidence"] += 0.1
    
    # Log the extraction result
    if result["datetime"]:
        logger.info(f"Extracted date/time: {result['datetime']} from text: '{text}' with confidence: {result['confidence']}")
    else:
        logger.warning(f"Failed to extract date/time from text: '{text}'")
    
    return result
