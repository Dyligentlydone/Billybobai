from typing import Dict, Optional
from datetime import datetime, timedelta
import json
import os

class CostTracker:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize cost tracker with optional config path
        Default costs based on current Twilio and OpenAI pricing
        """
        self.config_path = config_path or 'cost_config.json'
        self.default_config = {
            'sms': {
                'base_cost': 0.0075,  # Cost per SMS segment
                'segment_size': 160,   # Characters per segment
                'international_multiplier': 2.0  # Multiplier for international
            },
            'openai': {
                'gpt4': {
                    'input': 0.03,    # Cost per 1K input tokens
                    'output': 0.06    # Cost per 1K output tokens
                },
                'gpt35': {
                    'input': 0.0015,  # Cost per 1K input tokens
                    'output': 0.002   # Cost per 1K output tokens
                }
            },
            'volume_discounts': [
                {'threshold': 1000, 'discount': 0.05},  # 5% off above 1000 msgs
                {'threshold': 5000, 'discount': 0.10},  # 10% off above 5000 msgs
                {'threshold': 10000, 'discount': 0.15}  # 15% off above 10000 msgs
            ]
        }
        self.config = self._load_config()
        self.usage_data = {}
        
    def _load_config(self) -> Dict:
        """Load cost configuration from file or use defaults"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cost config: {e}")
        return self.default_config
        
    def calculate_message_costs(self,
                              business_id: str,
                              message_length: int,
                              token_counts: Dict[str, int],
                              model: str = 'gpt35',
                              is_international: bool = False) -> Dict[float, str]:
        """
        Calculate costs for a single message
        Returns breakdown of SMS and AI costs
        """
        # Calculate SMS cost
        sms_config = self.config['sms']
        segments = (message_length - 1) // sms_config['segment_size'] + 1
        base_sms_cost = segments * sms_config['base_cost']
        
        if is_international:
            base_sms_cost *= sms_config['international_multiplier']
            
        # Calculate AI cost
        ai_config = self.config['openai'][model]
        ai_cost = (
            (token_counts['input'] * ai_config['input'] +
             token_counts['output'] * ai_config['output']) / 1000
        )
        
        # Apply volume discounts if applicable
        total_cost = base_sms_cost + ai_cost
        discount = self._calculate_volume_discount(business_id)
        if discount > 0:
            total_cost *= (1 - discount)
        
        return {
            'sms_cost': base_sms_cost,
            'ai_cost': ai_cost,
            'discount': discount,
            'total_cost': total_cost
        }
    
    def _calculate_volume_discount(self, business_id: str) -> float:
        """Calculate volume discount based on usage"""
        if business_id not in self.usage_data:
            return 0
            
        # Get monthly message count
        monthly_messages = sum(
            count for date, count in self.usage_data[business_id]['messages'].items()
            if datetime.fromisoformat(date) > datetime.now() - timedelta(days=30)
        )
        
        # Find applicable discount
        for tier in reversed(self.config['volume_discounts']):
            if monthly_messages >= tier['threshold']:
                return tier['discount']
                
        return 0
    
    def update_usage(self, business_id: str, costs: Dict[str, float]) -> None:
        """Update usage data for a business"""
        today = datetime.now().date().isoformat()
        
        if business_id not in self.usage_data:
            self.usage_data[business_id] = {
                'messages': {},
                'costs': {
                    'sms': {},
                    'ai': {},
                    'total': {}
                }
            }
        
        usage = self.usage_data[business_id]
        
        # Update message count
        usage['messages'][today] = usage['messages'].get(today, 0) + 1
        
        # Update costs
        for cost_type in ['sms', 'ai', 'total']:
            if cost_type not in costs:
                continue
            usage['costs'][cost_type][today] = (
                usage['costs'][cost_type].get(today, 0) + costs[f'{cost_type}_cost']
            )
    
    def get_business_costs(self, business_id: str, 
                          days: int = 30) -> Dict[str, Dict]:
        """Get cost summary for a business"""
        if business_id not in self.usage_data:
            return {
                'message_volume': 0,
                'costs': {
                    'sms': 0,
                    'ai': 0,
                    'total': 0
                },
                'average_cost_per_message': 0
            }
        
        usage = self.usage_data[business_id]
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        # Calculate totals
        message_volume = sum(
            count for date, count in usage['messages'].items()
            if datetime.fromisoformat(date).date() >= start_date
        )
        
        costs = {
            cost_type: sum(
                amount for date, amount in amounts.items()
                if datetime.fromisoformat(date).date() >= start_date
            )
            for cost_type, amounts in usage['costs'].items()
        }
        
        return {
            'message_volume': message_volume,
            'costs': costs,
            'average_cost_per_message': (
                costs['total'] / message_volume if message_volume > 0 else 0
            )
        }
    
    def export_cost_report(self, business_id: str, 
                          start_date: datetime,
                          end_date: datetime) -> Dict:
        """Generate a detailed cost report for a date range"""
        if business_id not in self.usage_data:
            return {}
            
        usage = self.usage_data[business_id]
        report_data = {
            'daily_breakdown': {},
            'totals': {
                'messages': 0,
                'sms_cost': 0,
                'ai_cost': 0,
                'total_cost': 0
            }
        }
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.date().isoformat()
            
            daily_data = {
                'messages': usage['messages'].get(date_str, 0),
                'sms_cost': usage['costs']['sms'].get(date_str, 0),
                'ai_cost': usage['costs']['ai'].get(date_str, 0),
                'total_cost': usage['costs']['total'].get(date_str, 0)
            }
            
            report_data['daily_breakdown'][date_str] = daily_data
            
            # Update totals
            report_data['totals']['messages'] += daily_data['messages']
            report_data['totals']['sms_cost'] += daily_data['sms_cost']
            report_data['totals']['ai_cost'] += daily_data['ai_cost']
            report_data['totals']['total_cost'] += daily_data['total_cost']
            
            current_date += timedelta(days=1)
        
        return report_data
