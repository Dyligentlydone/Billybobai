from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import deque
from utils.slack_alerts import SlackAlerter

class MonitoringService:
    def __init__(self, config: Dict):
        self.config = config
        self.metrics = {
            'response_times': deque(maxlen=1000),  # Last 1000 response times
            'errors': deque(maxlen=1000),          # Last 1000 errors
            'daily_messages': 0,                   # Reset daily
            'last_reset': datetime.now()
        }
        
        # Initialize Slack alerter if configured
        self.alerter = None
        if (config.get('slackNotifications', {}).get('enabled') and 
            config['slackNotifications']['webhookUrl'] and 
            config['slackNotifications']['channel']):
            self.alerter = SlackAlerter(
                webhook_url=config['slackNotifications']['webhookUrl'],
                channel=config['slackNotifications']['channel'],
                mention_user=config['slackNotifications'].get('mentionUser')
            )
            # Test the connection
            self.alerter.test_connection()

    def record_response_time(self, response_time: int) -> None:
        """Record a response time and check if it exceeds threshold"""
        self.metrics['response_times'].append(response_time)
        
        if self.alerter and response_time > self.config['alertThresholds']['responseTime']:
            self.alerter.alert_response_time(
                response_time,
                self.config['alertThresholds']['responseTime']
            )

    def record_error(self, error: str) -> None:
        """Record an error and check error rate"""
        self.metrics['errors'].append(error)
        
        if not self.alerter:
            return
            
        # Calculate error rate over last 100 messages
        recent_messages = len(self.metrics['response_times'])
        if recent_messages >= 100:
            error_rate = (len(self.metrics['errors']) / recent_messages) * 100
            if error_rate > self.config['alertThresholds']['errorRate']:
                self.alerter.alert_error_rate(
                    error_rate,
                    self.config['alertThresholds']['errorRate']
                )

    def record_message(self) -> None:
        """Record a message and check daily volume"""
        # Reset counter if it's a new day
        if datetime.now() - self.metrics['last_reset'] > timedelta(days=1):
            self.metrics['daily_messages'] = 0
            self.metrics['last_reset'] = datetime.now()
        
        self.metrics['daily_messages'] += 1
        
        if (self.alerter and 
            self.metrics['daily_messages'] > self.config['alertThresholds']['dailyVolume']):
            self.alerter.alert_daily_volume(
                self.metrics['daily_messages'],
                self.config['alertThresholds']['dailyVolume']
            )

    def get_metrics(self) -> Dict:
        """Get current metrics"""
        if not self.metrics['response_times']:
            return {
                'average_response_time': 0,
                'error_rate': 0,
                'daily_messages': self.metrics['daily_messages']
            }
            
        recent_messages = len(self.metrics['response_times'])
        return {
            'average_response_time': sum(self.metrics['response_times']) / recent_messages,
            'error_rate': (len(self.metrics['errors']) / recent_messages) * 100,
            'daily_messages': self.metrics['daily_messages']
        }

    def update_config(self, new_config: Dict) -> None:
        """Update monitoring configuration"""
        self.config = new_config
        
        # Reinitialize Slack alerter with new config
        if (new_config.get('slackNotifications', {}).get('enabled') and 
            new_config['slackNotifications']['webhookUrl'] and 
            new_config['slackNotifications']['channel']):
            self.alerter = SlackAlerter(
                webhook_url=new_config['slackNotifications']['webhookUrl'],
                channel=new_config['slackNotifications']['channel'],
                mention_user=new_config['slackNotifications'].get('mentionUser')
            )
            # Test the connection with new config
            self.alerter.test_connection()
        else:
            self.alerter = None
