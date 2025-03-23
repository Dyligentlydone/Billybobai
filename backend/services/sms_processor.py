from typing import Dict, Optional, Tuple, NamedTuple
import time
from datetime import datetime
from routes.monitoring import record_message_metrics
from utils.openai_client import generate_response
from utils.message_quality import MessageQualityAnalyzer
from utils.cost_tracking import CostTracker
from twilio.rest import Client as TwilioClient
import logging

class ProcessingResult(NamedTuple):
    success: bool
    response: Optional[str]
    error: Optional[str]
    message_sid: Optional[str]
    sent_via_api: bool

class SMSProcessor:
    def __init__(self, business_id: str, workflow_id: str, workflow_name: str, config: Dict):
        """Initialize SMS processor with business and workflow info"""
        self.business_id = business_id
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.config = config
        
        # Initialize Twilio client
        self.twilio_client = TwilioClient(
            config['twilio']['account_sid'],
            config['twilio']['auth_token']
        )
        
        # Initialize quality analyzer and cost tracker
        self.quality_analyzer = MessageQualityAnalyzer()
        self.cost_tracker = CostTracker()
        
        # Get monitoring thresholds
        self.thresholds = config.get('monitoring', {}).get('alertThresholds', {
            'response_time': 5000,     # 5 seconds default
            'ai_time': 3000,          # 3 seconds default
            'min_confidence': 0.7,     # 70% confidence default
            'min_sentiment': 0.3,      # 30% positive sentiment default
            'min_relevance': 0.8,      # 80% relevance default
            'min_quality_score': 0.7,  # 70% quality score default
            'daily_cost': 100,         # $100 daily cost default
            'errorRate': 5,            # 5% error rate default
            'dailyVolume': 1000        # 1000 messages default
        })

    async def process_incoming_message(
        self, 
        from_number: str, 
        message_body: str,
        use_twiml: bool = False
    ) -> ProcessingResult:
        """
        Process an incoming SMS message and optionally send AI-generated response
        Args:
            from_number: Sender's phone number
            message_body: Content of the message
            use_twiml: If True, return response for TwiML instead of sending via API
        Returns: 
            ProcessingResult containing success status, response text, error (if any),
            message SID (if sent via API), and whether message was sent via API
        """
        start_time = time.time()
        error = None
        metrics = {}
        message_sid = None
        response = None
        
        try:
            # Generate AI response
            ai_start_time = time.time()
            response, ai_metrics = await generate_response(
                message_body,
                self.config['ai']['prompt_template'],
                self.config['ai']['brand_voice']
            )
            ai_time = int((time.time() - ai_start_time) * 1000)
            
            # Analyze message quality
            quality_metrics = self.quality_analyzer.analyze_message_quality(
                self.business_id,
                self.workflow_id,
                message_body,
                response
            )
            
            # Calculate costs
            cost_metrics = self.cost_tracker.calculate_message_costs(
                business_id=self.business_id,
                message_length=len(response),
                token_counts={
                    'input': ai_metrics['prompt_tokens'],
                    'output': ai_metrics['completion_tokens']
                },
                model=self.config['ai'].get('model', 'gpt35'),
                is_international=self._is_international(from_number)
            )
            
            # Send response via Twilio API if not using TwiML
            if not use_twiml:
                twilio_message = self.twilio_client.messages.create(
                    body=response,
                    from_=self.config['twilio']['phone_number'],
                    to=from_number,
                    status_callback=f"{self.config['twilio']['status_callback_url']}/{self.workflow_id}"
                )
                message_sid = twilio_message.sid
                logging.info(f"Sent message via Twilio API. SID: {message_sid}")
            
            # Update cost tracking
            self.cost_tracker.update_usage(self.business_id, cost_metrics)
            
            # Compile all metrics
            metrics = {
                'response_time': int((time.time() - start_time) * 1000),
                'ai_time': ai_time,
                'tokens': ai_metrics['total_tokens'],
                'confidence': ai_metrics.get('confidence', 1.0),
                'sentiment': quality_metrics['customer_metrics']['sentiment'],
                'relevance': quality_metrics['response_metrics']['context_relevance'],
                'quality_score': quality_metrics['quality_score'],
                'is_follow_up': quality_metrics['is_follow_up'],
                'sms_cost': cost_metrics['sms_cost'],
                'ai_cost': cost_metrics['ai_cost'],
                'total_cost': cost_metrics['total_cost'],
                'message_sid': message_sid,
                'sent_via_api': not use_twiml,
                # Additional quality metrics
                'tone_match': quality_metrics['response_metrics']['tone_match'],
                'completeness': quality_metrics['response_metrics']['completeness'],
                'personalization': quality_metrics['response_metrics']['personalization'],
                'clarity': quality_metrics['response_metrics']['clarity'],
                'customer_urgency': quality_metrics['customer_metrics']['urgency']
            }
            
        except Exception as e:
            error = str(e)
            logging.error(f"Error processing message: {error}")
            
            # Get fallback message
            response = self.get_fallback_message()
            
            # Send fallback via API if not using TwiML
            if not use_twiml and response:
                try:
                    twilio_message = self.twilio_client.messages.create(
                        body=response,
                        from_=self.config['twilio']['phone_number'],
                        to=from_number,
                        status_callback=f"{self.config['twilio']['status_callback_url']}/{self.workflow_id}"
                    )
                    message_sid = twilio_message.sid
                    logging.info(f"Sent fallback message via Twilio API. SID: {message_sid}")
                except Exception as fallback_error:
                    error = f"Original error: {error}. Fallback error: {str(fallback_error)}"
                    logging.error(f"Failed to send fallback message: {error}")
        
        finally:
            # Add error to metrics if present
            if error:
                metrics['error'] = error
            
            # Record all metrics
            record_message_metrics(
                business_id=self.business_id,
                workflow_id=self.workflow_id,
                workflow_name=self.workflow_name,
                thresholds=self.thresholds,
                metrics=metrics
            )
        
        return ProcessingResult(
            success=error is None,
            response=response,
            error=error,
            message_sid=message_sid,
            sent_via_api=not use_twiml
        )

    def get_fallback_message(self) -> str:
        """Get the configured fallback message"""
        return self.config.get('fallback_message', 
            "We're sorry, but we couldn't process your message at this time. Please try again later."
        )

    def process_delivery_status(self, message_sid: str, status: str, error_code: Optional[str] = None) -> None:
        """Process message delivery status updates"""
        if status in ['failed', 'undelivered']:
            error = f"Message delivery failed. Status: {status}"
            if error_code:
                error += f", Error code: {error_code}"
            
            logging.error(f"Message delivery failed. SID: {message_sid}. {error}")
            
            # Record the error with minimal metrics
            record_message_metrics(
                business_id=self.business_id,
                workflow_id=self.workflow_id,
                workflow_name=self.workflow_name,
                thresholds=self.thresholds,
                metrics={
                    'error': error,
                    'message_sid': message_sid,
                    'delivery_status': status,
                    'error_code': error_code
                }
            )
    
    def _is_international(self, phone_number: str) -> bool:
        """Check if a phone number is international (non-US)"""
        # Remove any formatting
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Check if it's a US number (including +1)
        return not (cleaned.startswith('1') and len(cleaned) == 11 or len(cleaned) == 10)
