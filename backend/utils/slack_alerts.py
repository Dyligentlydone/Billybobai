import requests
from typing import Optional
from datetime import datetime

class SlackAlerter:
    def __init__(self, 
                 webhook_url: str, 
                 channel: str, 
                 business_name: str,
                 environment: str,
                 mention_user: Optional[str] = None,
                 use_shared_workspace: bool = False):
        self.webhook_url = webhook_url
        self.channel = channel.lstrip('#')
        self.business_name = business_name
        self.environment = environment
        self.mention_user = mention_user.lstrip('@') if mention_user else None
        self.use_shared_workspace = use_shared_workspace

    def _get_environment_emoji(self) -> str:
        """Get emoji based on environment"""
        return "🚀" if self.environment == "production" else "🔧"

    def _format_header(self) -> str:
        """Format the header with business and environment info"""
        env_emoji = self._get_environment_emoji()
        return f"{env_emoji} *{self.business_name}* ({self.environment})"

    def send_alert(self, title: str, message: str, is_critical: bool = False) -> bool:
        """
        Send an alert to Slack.
        Returns True if successful, False otherwise.
        """
        try:
            # Add user mention for critical alerts
            if is_critical and self.mention_user:
                message = f"@{self.mention_user} {message}"

            header = self._format_header()
            
            # For shared workspaces, always include business name in channel
            if self.use_shared_workspace:
                channel = f"#{self.business_name.lower()}-{self.channel}"
            else:
                channel = f"#{self.channel}"

            payload = {
                "channel": channel,
                "attachments": [{
                    "color": "#ff0000" if is_critical else "#36a64f",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": header
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*{title}*\n{message}"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"Sent by SMS Automation Monitor • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                                }
                            ]
                        }
                    ]
                }]
            }

            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Slack alert: {str(e)}")
            return False

    def alert_response_time(self, response_time: int, threshold: int, workflow_name: str) -> bool:
        """Alert when response time exceeds threshold"""
        is_critical = response_time > threshold * 1.5  # 50% over threshold is critical
        title = "🚨 High Response Time" if is_critical else "⚠️ Slow Response Time"
        message = (
            f"*Workflow:* {workflow_name}\n"
            f"Response time of {response_time}ms exceeds threshold of {threshold}ms\n"
            f"This could impact user experience and satisfaction."
        )
        return self.send_alert(title, message, is_critical)

    def alert_error_rate(self, error_rate: float, threshold: float, workflow_name: str) -> bool:
        """Alert when error rate exceeds threshold"""
        is_critical = error_rate > threshold * 1.5  # 50% over threshold is critical
        title = "🚨 Critical Error Rate" if is_critical else "⚠️ High Error Rate"
        message = (
            f"*Workflow:* {workflow_name}\n"
            f"Error rate of {error_rate}% exceeds threshold of {threshold}%\n"
            f"This indicates potential system issues that need attention."
        )
        return self.send_alert(title, message, is_critical)

    def alert_daily_volume(self, volume: int, threshold: int, workflow_name: str) -> bool:
        """Alert when daily message volume exceeds threshold"""
        is_critical = volume > threshold * 1.2  # 20% over threshold is critical
        title = "🚨 Volume Limit Critical" if is_critical else "⚠️ High Message Volume"
        message = (
            f"*Workflow:* {workflow_name}\n"
            f"Daily message volume of {volume} exceeds threshold of {threshold}\n"
            f"This may impact costs and system performance."
        )
        return self.send_alert(title, message, is_critical)

    def test_connection(self) -> bool:
        """Test the Slack webhook connection"""
        title = "🔧 Monitor Configuration"
        message = (
            "*SMS Automation monitoring has been configured successfully.*\n\n"
            f"Alerts will be sent to #{self.channel}\n"
        )
        if self.mention_user:
            message += f"Critical alerts will mention @{self.mention_user}\n"
        
        if self.use_shared_workspace:
            message += f"\nUsing shared workspace mode - alerts will be sent to #{self.business_name.lower()}-{self.channel}"
            
        return self.send_alert(title, message, False)
