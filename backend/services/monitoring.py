from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from utils.slack_alerts import SlackAlerter

class BusinessMetrics:
    def __init__(self):
        self.workflows = defaultdict(WorkflowMetrics)
        self.total_messages = 0
        self.total_errors = 0
        self.total_cost = 0.0
        # New: AI metrics aggregation
        self.total_tokens = 0
        self.total_ai_time = 0
        self.avg_confidence = 0.0
        # New: Quality metrics aggregation
        self.avg_sentiment = 0.0
        self.avg_relevance = 0.0
        self.follow_up_rate = 0.0

class WorkflowMetrics:
    def __init__(self):
        self.name = ""
        self.response_times = []
        self.errors = []
        self.daily_messages = 0
        self.last_alert_time = None
        # New: AI metrics
        self.ai_response_times = []
        self.token_counts = []
        self.confidence_scores = []
        # New: Quality metrics
        self.sentiment_scores = []
        self.relevance_scores = []
        self.follow_up_counts = 0
        # New: Cost tracking
        self.sms_cost = 0.0
        self.ai_cost = 0.0

class MonitoringService:
    def __init__(self):
        self.business_metrics: Dict[str, BusinessMetrics] = defaultdict(BusinessMetrics)
        self.alerters: Dict[str, SlackAlerter] = {}

    def configure_business(self, business_id: str, config: Dict) -> None:
        """Configure monitoring for a business"""
        if 'slack' in config:
            self.alerters[business_id] = SlackAlerter(
                webhook_url=config['slack']['webhook_url'],
                channel=config['slack'].get('channel'),
                mention_user=config['slack'].get('mention_user'),
                business_name=config.get('business_name', 'Unknown Business'),
                environment=config.get('environment', 'production')
            )

    def record_message(self, business_id: str, workflow_id: str, workflow_name: str, 
                      thresholds: Dict, metrics: Dict) -> None:
        """
        Record message metrics including AI, quality, and cost metrics
        
        metrics: {
            'response_time': int,
            'ai_time': int,
            'tokens': int,
            'confidence': float,
            'sentiment': float,
            'relevance': float,
            'is_follow_up': bool,
            'sms_cost': float,
            'ai_cost': float,
            'error': Optional[str]
        }
        """
        business = self.business_metrics[business_id]
        workflow = business.workflows[workflow_id]
        workflow.name = workflow_name
        
        # Basic metrics
        if metrics.get('response_time'):
            workflow.response_times.append(metrics['response_time'])
        if metrics.get('error'):
            workflow.errors.append(metrics['error'])
        workflow.daily_messages += 1
        business.total_messages += 1
        
        # AI metrics
        if metrics.get('ai_time'):
            workflow.ai_response_times.append(metrics['ai_time'])
            business.total_ai_time += metrics['ai_time']
        if metrics.get('tokens'):
            workflow.token_counts.append(metrics['tokens'])
            business.total_tokens += metrics['tokens']
        if metrics.get('confidence'):
            workflow.confidence_scores.append(metrics['confidence'])
            business.avg_confidence = sum(workflow.confidence_scores) / len(workflow.confidence_scores)
        
        # Quality metrics
        if metrics.get('sentiment'):
            workflow.sentiment_scores.append(metrics['sentiment'])
            business.avg_sentiment = sum(workflow.sentiment_scores) / len(workflow.sentiment_scores)
        if metrics.get('relevance'):
            workflow.relevance_scores.append(metrics['relevance'])
            business.avg_relevance = sum(workflow.relevance_scores) / len(workflow.relevance_scores)
        if metrics.get('is_follow_up'):
            workflow.follow_up_counts += 1
            workflow.follow_up_rate = workflow.follow_up_counts / workflow.daily_messages
        
        # Cost tracking
        if metrics.get('sms_cost'):
            workflow.sms_cost += metrics['sms_cost']
        if metrics.get('ai_cost'):
            workflow.ai_cost += metrics['ai_cost']
        business.total_cost = sum(w.sms_cost + w.ai_cost for w in business.workflows.values())
        
        # Check thresholds and alert if needed
        self._check_thresholds(business_id, workflow_id, workflow_name, thresholds, metrics)

    def _check_thresholds(self, business_id: str, workflow_id: str, workflow_name: str, 
                         thresholds: Dict, metrics: Dict) -> None:
        """Check all thresholds and send alerts if needed"""
        if business_id not in self.alerters:
            return
            
        alerter = self.alerters[business_id]
        workflow = self.business_metrics[business_id].workflows[workflow_id]
        
        # Don't alert more than once per minute for the same workflow
        if workflow.last_alert_time and \
           datetime.now() - workflow.last_alert_time < timedelta(minutes=1):
            return
            
        alerts = []
        
        # Response time alerts
        if metrics.get('response_time', 0) > thresholds.get('response_time', 5000):
            alerts.append(f"High response time: {metrics['response_time']}ms")
            
        # AI performance alerts
        if metrics.get('confidence', 1.0) < thresholds.get('min_confidence', 0.7):
            alerts.append(f"Low confidence score: {metrics['confidence']:.2f}")
        if metrics.get('ai_time', 0) > thresholds.get('ai_time', 3000):
            alerts.append(f"High AI processing time: {metrics['ai_time']}ms")
            
        # Quality alerts
        if metrics.get('sentiment', 1.0) < thresholds.get('min_sentiment', 0.3):
            alerts.append(f"Low customer sentiment: {metrics['sentiment']:.2f}")
        if metrics.get('relevance', 1.0) < thresholds.get('min_relevance', 0.8):
            alerts.append(f"Low response relevance: {metrics['relevance']:.2f}")
            
        # Cost alerts
        daily_cost = workflow.sms_cost + workflow.ai_cost
        if daily_cost > thresholds.get('daily_cost', 100):
            alerts.append(f"High daily cost: ${daily_cost:.2f}")
            
        # Send alert if any thresholds exceeded
        if alerts:
            workflow.last_alert_time = datetime.now()
            alert_message = f"⚠️ {workflow_name} Alerts:\n" + "\n".join(f"• {alert}" for alert in alerts)
            alerter.send_alert(alert_message)

    def get_workflow_metrics(self, business_id: str, workflow_id: str) -> Dict:
        """Get metrics for a specific workflow"""
        workflow = self.business_metrics[business_id].workflows[workflow_id]
        return {
            'name': workflow.name,
            'response_times': {
                'avg': sum(workflow.response_times) / len(workflow.response_times) if workflow.response_times else 0,
                'max': max(workflow.response_times) if workflow.response_times else 0
            },
            'ai_metrics': {
                'avg_time': sum(workflow.ai_response_times) / len(workflow.ai_response_times) if workflow.ai_response_times else 0,
                'avg_tokens': sum(workflow.token_counts) / len(workflow.token_counts) if workflow.token_counts else 0,
                'avg_confidence': sum(workflow.confidence_scores) / len(workflow.confidence_scores) if workflow.confidence_scores else 0
            },
            'quality_metrics': {
                'avg_sentiment': sum(workflow.sentiment_scores) / len(workflow.sentiment_scores) if workflow.sentiment_scores else 0,
                'avg_relevance': sum(workflow.relevance_scores) / len(workflow.relevance_scores) if workflow.relevance_scores else 0,
                'follow_up_rate': workflow.follow_up_rate
            },
            'costs': {
                'sms_cost': workflow.sms_cost,
                'ai_cost': workflow.ai_cost,
                'total_cost': workflow.sms_cost + workflow.ai_cost
            },
            'errors': len(workflow.errors),
            'daily_messages': workflow.daily_messages
        }

    def get_business_metrics(self, business_id: str) -> Dict:
        """Get aggregated metrics for an entire business"""
        business = self.business_metrics[business_id]
        return {
            'total_messages': business.total_messages,
            'total_errors': business.total_errors,
            'ai_metrics': {
                'total_tokens': business.total_tokens,
                'avg_confidence': business.avg_confidence
            },
            'quality_metrics': {
                'avg_sentiment': business.avg_sentiment,
                'avg_relevance': business.avg_relevance
            },
            'costs': {
                'total_cost': business.total_cost
            },
            'workflows': {
                workflow_id: self.get_workflow_metrics(business_id, workflow_id)
                for workflow_id in business.workflows
            }
        }
