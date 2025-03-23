import requests
from typing import Optional
from datetime import datetime

class SlackAlerter:
    def __init__(self, webhook_url: str, channel: str, mention_user: Optional[str] = None):
        self.webhook_url = webhook_url
        self.channel = channel.lstrip('#')  # Remove # if present
        self.mention_user = mention_user.lstrip('@') if mention_user else None

    def send_alert(self, title: str, message: str, is_critical: bool = False) -> bool:
        """
        Send an alert to Slack.
        Returns True if successful, False otherwise.
        """
        try:
            # Add user mention for critical alerts
            if is_critical and self.mention_user:
                message = f"@{self.mention_user} {message}"

            payload = {
                "channel": f"#{self.channel}",
                "attachments": [{
                    "color": "#ff0000" if is_critical else "#36a64f",
                    "title": title,
                    "text": message,
                    "footer": "SMS Automation Monitor",
                    "ts": int(datetime.now().timestamp())
                }]
            }

            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Slack alert: {str(e)}")
            return False

    def alert_response_time(self, response_time: int, threshold: int) -> bool:
        """Alert when response time exceeds threshold"""
        is_critical = response_time > threshold * 1.5  # 50% over threshold is critical
        title = "🚨 High Response Time" if is_critical else "⚠️ Slow Response Time"
        message = (
            f"Response time of {response_time}ms exceeds threshold of {threshold}ms\n"
            f"This could impact user experience and satisfaction."
        )
        return self.send_alert(title, message, is_critical)

    def alert_error_rate(self, error_rate: float, threshold: float) -> bool:
        """Alert when error rate exceeds threshold"""
        is_critical = error_rate > threshold * 1.5  # 50% over threshold is critical
        title = "🚨 Critical Error Rate" if is_critical else "⚠️ High Error Rate"
        message = (
            f"Error rate of {error_rate}% exceeds threshold of {threshold}%\n"
            f"This indicates potential system issues that need attention."
        )
        return self.send_alert(title, message, is_critical)

    def alert_daily_volume(self, volume: int, threshold: int) -> bool:
        """Alert when daily message volume exceeds threshold"""
        is_critical = volume > threshold * 1.2  # 20% over threshold is critical
        title = "🚨 Volume Limit Critical" if is_critical else "⚠️ High Message Volume"
        message = (
            f"Daily message volume of {volume} exceeds threshold of {threshold}\n"
            f"This may impact costs and system performance."
        )
        return self.send_alert(title, message, is_critical)

    def test_connection(self) -> bool:
        """Test the Slack webhook connection"""
        title = "🔧 Monitor Configuration"
        message = (
            "SMS Automation monitoring has been configured successfully.\n"
            f"Alerts will be sent to #{self.channel}"
        )
        if self.mention_user:
            message += f"\nCritical alerts will mention @{self.mention_user}"
            
        return self.send_alert(title, message, False)
