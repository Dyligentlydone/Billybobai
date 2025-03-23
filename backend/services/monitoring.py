from typing import Dict, Optional, NamedTuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
from utils.slack_alerts import SlackAlerter

class WorkflowMetrics:
    def __init__(self):
        self.response_times = deque(maxlen=1000)  # Last 1000 response times
        self.errors = deque(maxlen=1000)          # Last 1000 errors
        self.daily_messages = 0                    # Reset daily
        self.last_reset = datetime.now()

class BusinessMetrics:
    def __init__(self):
        self.workflows = defaultdict(WorkflowMetrics)
        self.total_daily_messages = 0
        self.last_reset = datetime.now()

class MonitoringService:
    def __init__(self):
        self.business_metrics: Dict[str, BusinessMetrics] = defaultdict(BusinessMetrics)
        self.alerters: Dict[str, SlackAlerter] = {}

    def configure_business(self, business_id: str, config: Dict) -> None:
        """Configure monitoring for a business"""
        if config.get('slackNotifications', {}).get('enabled'):
            slack_config = config['slackNotifications']
            self.alerters[business_id] = SlackAlerter(
                webhook_url=slack_config['webhookUrl'],
                channel=slack_config['channel'],
                business_name=config['businessName'],
                environment=config.get('environment', 'production'),
                mention_user=slack_config.get('mentionUser'),
                use_shared_workspace=slack_config.get('useSharedWorkspace', False)
            )
            # Test the connection
            self.alerters[business_id].test_connection()

    def record_response_time(self, business_id: str, workflow_id: str, workflow_name: str, response_time: int, thresholds: Dict) -> None:
        """Record a response time and check if it exceeds threshold"""
        metrics = self.business_metrics[business_id].workflows[workflow_id]
        metrics.response_times.append(response_time)
        
        alerter = self.alerters.get(business_id)
        if alerter and response_time > thresholds['responseTime']:
            alerter.alert_response_time(
                response_time,
                thresholds['responseTime'],
                workflow_name
            )

    def record_error(self, business_id: str, workflow_id: str, workflow_name: str, error: str, thresholds: Dict) -> None:
        """Record an error and check error rate"""
        metrics = self.business_metrics[business_id].workflows[workflow_id]
        metrics.errors.append(error)
        
        alerter = self.alerters.get(business_id)
        if not alerter:
            return
            
        # Calculate error rate over last 100 messages
        recent_messages = len(metrics.response_times)
        if recent_messages >= 100:
            error_rate = (len(metrics.errors) / recent_messages) * 100
            if error_rate > thresholds['errorRate']:
                alerter.alert_error_rate(
                    error_rate,
                    thresholds['errorRate'],
                    workflow_name
                )

    def record_message(self, business_id: str, workflow_id: str, workflow_name: str, thresholds: Dict) -> None:
        """Record a message and check daily volume"""
        business = self.business_metrics[business_id]
        workflow = business.workflows[workflow_id]
        
        # Reset counters if it's a new day
        now = datetime.now()
        if now - workflow.last_reset > timedelta(days=1):
            workflow.daily_messages = 0
            workflow.last_reset = now
            
        if now - business.last_reset > timedelta(days=1):
            business.total_daily_messages = 0
            business.last_reset = now
        
        # Update counters
        workflow.daily_messages += 1
        business.total_daily_messages += 1
        
        alerter = self.alerters.get(business_id)
        if alerter:
            # Alert on workflow-level volume
            if workflow.daily_messages > thresholds['dailyVolume']:
                alerter.alert_daily_volume(
                    workflow.daily_messages,
                    thresholds['dailyVolume'],
                    workflow_name
                )
            
            # Alert on business-level volume if it's 50% higher than the sum of all workflow thresholds
            total_threshold = thresholds['dailyVolume'] * len(business.workflows)
            if business.total_daily_messages > total_threshold * 1.5:
                alerter.send_alert(
                    "🚨 Business-wide Volume Alert",
                    f"Total daily message volume ({business.total_daily_messages}) across all workflows is 50% higher than expected ({total_threshold})",
                    True
                )

    def get_workflow_metrics(self, business_id: str, workflow_id: str) -> Dict:
        """Get metrics for a specific workflow"""
        metrics = self.business_metrics[business_id].workflows[workflow_id]
        
        if not metrics.response_times:
            return {
                'average_response_time': 0,
                'error_rate': 0,
                'daily_messages': metrics.daily_messages
            }
            
        recent_messages = len(metrics.response_times)
        return {
            'average_response_time': sum(metrics.response_times) / recent_messages,
            'error_rate': (len(metrics.errors) / recent_messages) * 100,
            'daily_messages': metrics.daily_messages
        }

    def get_business_metrics(self, business_id: str) -> Dict:
        """Get aggregated metrics for an entire business"""
        business = self.business_metrics[business_id]
        
        total_response_times = []
        total_errors = []
        
        for workflow in business.workflows.values():
            total_response_times.extend(workflow.response_times)
            total_errors.extend(workflow.errors)
            
        if not total_response_times:
            return {
                'average_response_time': 0,
                'error_rate': 0,
                'total_daily_messages': business.total_daily_messages,
                'workflow_count': len(business.workflows)
            }
            
        return {
            'average_response_time': sum(total_response_times) / len(total_response_times),
            'error_rate': (len(total_errors) / len(total_response_times)) * 100,
            'total_daily_messages': business.total_daily_messages,
            'workflow_count': len(business.workflows)
        }
