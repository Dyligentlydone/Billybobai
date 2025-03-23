import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

class CostTracker:
    def __init__(self):
        """Initialize cost tracker"""
        self.daily_costs = {}  # business_id -> {date -> cost}
        self.message_costs = {}  # business_id -> {message_id -> cost}
        
    def track_message_cost(
        self,
        business_id: str,
        message_id: str,
        ai_cost: float,
        sms_cost: float = 0.0075  # Default Twilio cost per segment
    ) -> None:
        """Track cost for a specific message"""
        try:
            # Store message cost
            if business_id not in self.message_costs:
                self.message_costs[business_id] = {}
            
            total_cost = ai_cost + sms_cost
            self.message_costs[business_id][message_id] = total_cost
            
            # Update daily cost
            today = datetime.now().date()
            if business_id not in self.daily_costs:
                self.daily_costs[business_id] = {}
            
            if today not in self.daily_costs[business_id]:
                self.daily_costs[business_id][today] = 0.0
                
            self.daily_costs[business_id][today] += total_cost
            
            # Log cost
            logging.info(
                f"Cost for message {message_id}: "
                f"AI=${ai_cost:.4f}, SMS=${sms_cost:.4f}, "
                f"Total=${total_cost:.4f}"
            )
            
        except Exception as e:
            logging.error(f"Error tracking message cost: {str(e)}")
    
    def get_daily_cost(self, business_id: str, date: Optional[datetime] = None) -> float:
        """Get total cost for a specific day"""
        try:
            if date is None:
                date = datetime.now().date()
            
            return self.daily_costs.get(business_id, {}).get(date, 0.0)
            
        except Exception as e:
            logging.error(f"Error getting daily cost: {str(e)}")
            return 0.0
    
    def get_message_cost(self, business_id: str, message_id: str) -> float:
        """Get cost for a specific message"""
        try:
            return self.message_costs.get(business_id, {}).get(message_id, 0.0)
            
        except Exception as e:
            logging.error(f"Error getting message cost: {str(e)}")
            return 0.0
    
    def get_cost_summary(
        self,
        business_id: str,
        days: int = 30
    ) -> Dict[str, float]:
        """Get cost summary for the last N days"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get costs for date range
            costs = {}
            current_date = start_date
            while current_date <= end_date:
                costs[str(current_date)] = self.get_daily_cost(business_id, current_date)
                current_date += timedelta(days=1)
            
            # Calculate summary
            total_cost = sum(costs.values())
            avg_daily_cost = total_cost / days if days > 0 else 0
            
            return {
                'total_cost': total_cost,
                'average_daily_cost': avg_daily_cost,
                'daily_costs': costs
            }
            
        except Exception as e:
            logging.error(f"Error getting cost summary: {str(e)}")
            return {
                'total_cost': 0.0,
                'average_daily_cost': 0.0,
                'daily_costs': {}
            }
