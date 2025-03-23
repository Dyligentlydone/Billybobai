from typing import Dict, Optional, Tuple
import time
from datetime import datetime
from routes.monitoring import record_message_metrics
from utils.openai_client import generate_response
from twilio.rest import Client as TwilioClient

class SMSProcessor:
    def __init__(self, business_id: str, workflow_id: str, workflow_name: str, config: Dict):
        """
        Initialize SMS processor with business and workflow info
        """
        self.business_id = business_id
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.config = config
        
        # Initialize Twilio client
        self.twilio_client = TwilioClient(
            config['twilio']['account_sid'],
            config['twilio']['auth_token']
        )
        
        # Get monitoring thresholds
        self.thresholds = config.get('monitoring', {}).get('alertThresholds', {
            'responseTime': 5000,  # 5 seconds default
            'errorRate': 5,       # 5% default
            'dailyVolume': 1000   # 1000 messages default
        })

    async def process_incoming_message(self, from_number: str, message_body: str) -> Tuple[bool, Optional[str]]:
        """
        Process an incoming SMS message and send AI-generated response
        Returns: (success, error_message if any)
        """
        start_time = time.time()
        error = None
        
        try:
            # Generate AI response
            response = await generate_response(
                message_body,
                self.config['ai']['prompt_template'],
                self.config['ai']['brand_voice']
            )
            
            # Send response via Twilio
            message = self.twilio_client.messages.create(
                body=response,
                from_=self.config['twilio']['phone_number'],
                to=from_number
            )
            
            success = True
            
        except Exception as e:
            error = str(e)
            success = False
            
            # Send fallback message if configured
            if self.config.get('fallback_message'):
                try:
                    self.twilio_client.messages.create(
                        body=self.config['fallback_message'],
                        from_=self.config['twilio']['phone_number'],
                        to=from_number
                    )
                except Exception as fallback_error:
                    error = f"Original error: {error}. Fallback error: {str(fallback_error)}"
        
        finally:
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
            # Record metrics
            record_message_metrics(
                business_id=self.business_id,
                workflow_id=self.workflow_id,
                workflow_name=self.workflow_name,
                response_time=response_time,
                error=error,
                thresholds=self.thresholds
            )
        
        return success, error

    def process_delivery_status(self, message_sid: str, status: str) -> None:
        """
        Process message delivery status updates
        """
        if status in ['failed', 'undelivered']:
            error = f"Message delivery failed. Status: {status}"
            
            # Record the error
            record_message_metrics(
                business_id=self.business_id,
                workflow_id=self.workflow_id,
                workflow_name=self.workflow_name,
                response_time=0,  # Not applicable for delivery status
                error=error,
                thresholds=self.thresholds
            )
