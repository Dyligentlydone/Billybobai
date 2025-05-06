from typing import Dict, Optional, Tuple, NamedTuple, Any
import time
from datetime import datetime
import os
import json
import logging
from routes.monitoring import record_message_metrics
from utils.openai_client import initialize as init_openai, generate_response
from utils.message_quality import MessageQualityAnalyzer
from utils.cost_tracking import CostTracker
from twilio.rest import Client as TwilioClient
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User, Comment
from .retry_handler import RetryHandler
from .opt_out_handler import OptOutHandler
from app.models.business import Business
from app.models.workflow import Workflow
from app.models.email import EmailThread, InboundEmail

class ProcessingResult(NamedTuple):
    success: bool
    response: Optional[str]
    error: Optional[str]
    message_sid: Optional[str]
    ticket_id: Optional[int]
    sent_via_api: bool

class SMSProcessor:
    def __init__(self, business_id: str, workflow_id: str, workflow_name: str, config: Dict):
        """Initialize SMS processor with business and workflow info"""
        logging.info(f"[SMS_PROCESSOR] Initializing SMSProcessor for business_id={business_id}, workflow_id={workflow_id}, workflow_name={workflow_name}")
        self.business_id = business_id
        self.workflow_id = workflow_id
        self.workflow_name = workflow_name
        self.config = config
        logging.info(f"[SMS_PROCESSOR] Loaded config for workflow_id={workflow_id}: {json.dumps(config, indent=2, default=str)}")
        
        # Initialize OpenAI
        # Robustly fetch OpenAI API key from config['aiTraining']['openAIKey'],
        # or config['actions']['aiTraining']['openAIKey'], or environment
        openai_key = None
        if 'aiTraining' in config and isinstance(config['aiTraining'], dict):
            openai_key = config['aiTraining'].get('openAIKey')
        elif 'actions' in config and isinstance(config['actions'], dict):
            ai_training = config['actions'].get('aiTraining')
            if isinstance(ai_training, dict):
                openai_key = ai_training.get('openAIKey')
        if not openai_key:
            openai_key = os.getenv('OPENAI_API_KEY')
        init_openai(openai_key)
        
        # Initialize Twilio client
        self.twilio_client = TwilioClient(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        self.messaging_service_sid = os.getenv('TWILIO_MESSAGING_SERVICE_SID')
        
        # Initialize Zendesk client if configured
        self.zendesk_client = None
        if config.get('zendesk', {}).get('enabled', False):
            try:
                self.zendesk_client = Zenpy(
                    email=os.getenv('ZENDESK_EMAIL'),
                    token=os.getenv('ZENDESK_API_TOKEN'),
                    subdomain=os.getenv('ZENDESK_SUBDOMAIN')
                )
                logging.info(f"Initialized Zendesk client for workflow {workflow_id}")
            except Exception as e:
                logging.error(f"Failed to initialize Zendesk client: {str(e)}")
        
        # Initialize quality analyzer and cost tracker
        self.quality_analyzer = MessageQualityAnalyzer()
        self.cost_tracker = CostTracker()
        
        # Initialize retry handler
        self.retry_handler = RetryHandler(self.twilio_client, None)
        
        # Initialize opt-out handler
        self.opt_out_handler = OptOutHandler(None)
        
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

    async def create_zendesk_ticket(
        self,
        from_number: str,
        message_body: str,
        response: str
    ) -> Optional[int]:
        """Create a Zendesk ticket for the SMS interaction"""
        if not self.zendesk_client:
            return None
            
        try:
            # Try to find existing user by phone number
            users = self.zendesk_client.search(type='user', phone=from_number)
            
            if users:
                requester_id = next(users).id
            else:
                # Create new user if not found
                user = self.zendesk_client.users.create(User(
                    name=f"SMS User ({from_number})",
                    phone=from_number,
                    role="end-user"
                ))
                requester_id = user.id
            
            # Create ticket
            ticket = self.zendesk_client.tickets.create(Ticket(
                subject=f"SMS Conversation - {self.workflow_name}",
                requester_id=requester_id,
                tags=['sms', self.workflow_name, self.business_id],
                custom_fields=[
                    {'id': 'workflow_id', 'value': self.workflow_id},
                    {'id': 'business_id', 'value': self.business_id}
                ],
                comment=Comment(
                    body=f"""Customer Message:
{message_body}

AI Response:
{response}

Phone Number: {from_number}
Workflow: {self.workflow_name}
Business ID: {self.business_id}
"""
                )
            ))
            
            logging.info(f"Created Zendesk ticket {ticket.id} for message from {from_number}")
            return ticket.id
            
        except Exception as e:
            logging.error(f"Failed to create Zendesk ticket: {str(e)}")
            return None

    async def process_incoming_message(
        self, 
        from_number: str, 
        message_body: str,
        use_twiml: bool = False,
        metadata: Dict[str, Any] = None
    ) -> ProcessingResult:
        """Process an incoming SMS message and optionally send AI-generated response"""
        logging.info(f"[SMS_PROCESSOR] process_incoming_message called: business_id={self.business_id}, workflow_id={self.workflow_id}, from_number={from_number}, message_body={message_body}, use_twiml={use_twiml}")
        start_time = time.time()
        error = None
        metrics = {}
        message_sid = None
        response = None
        ticket_id = None
        
        try:
            logging.info(f"[SMS_PROCESSOR] Attempting to load Business and Workflow from DB")
            business = Business.query.filter_by(id=self.business_id).first()
            workflow = Workflow.query.filter_by(id=self.workflow_id).first()
            if not business:
                logging.error(f"[SMS_PROCESSOR] Business not found: business_id={self.business_id}")
            if not workflow:
                logging.error(f"[SMS_PROCESSOR] Workflow not found: workflow_id={self.workflow_id}")
            
            # Get business context
            context = {
                'business_name': self.config.get('business_name', ''),
                'workflow_name': self.workflow_name,
                'common_questions': self.config.get('common_questions', []),
                'product_info': self.config.get('product_info', {}),
                'tone': self.config.get('tone', 'professional')
            }
            
            # Generate AI response
            ai_start_time = time.time()
            result = await generate_response(
                message=message_body,
                context=context,
                tone=self.config.get('tone', 'professional'),
                model=self.config.get('ai_model', 'gpt-3.5-turbo')
            )
            
            response = result.text
            ai_time = int((time.time() - ai_start_time) * 1000)
            
            # Create Zendesk ticket if enabled
            if self.config.get('zendesk', {}).get('enabled', False):
                ticket_id = await self.create_zendesk_ticket(
                    from_number=from_number,
                    message_body=message_body,
                    response=response
                )
            
            # Send response via Twilio API if not using TwiML
            if not use_twiml:
                message_params = {
                    'body': response,
                    'to': from_number,
                    'status_callback': metadata.get('status_callback') if metadata else None
                }
                
                # Use either messaging service or phone number
                if self.messaging_service_sid:
                    message_params['messaging_service_sid'] = self.messaging_service_sid
                else:
                    message_params['from_'] = self.twilio_phone
                
                # Check if number is opted out
                if await self.opt_out_handler.is_opted_out(from_number, self.business_id):
                    self.logger.info(f"Skipping send to opted-out number: {from_number}")
                    return ProcessingResult(
                        success=True,
                        response=None,
                        error=None,
                        message_sid=None,
                        ticket_id=ticket_id,
                        sent_via_api=False
                    )
                
                twilio_message = await self.retry_handler.retry_send(
                    message_id=None,
                    to_number=from_number,
                    from_number=self.twilio_phone,
                    body=response,
                    attempt=1,
                    metadata=metadata
                )
                
                if twilio_message:
                    message_sid = twilio_message.sid
                    logging.info(f"Sent message via Twilio API. SID: {message_sid}")
            
            # Compile metrics
            metrics = {
                'response_time': int((time.time() - start_time) * 1000),
                'ai_time': ai_time,
                'tokens': result.tokens_used,
                'confidence': result.confidence,
                'cost': result.cost,
                'model': result.model_used,
                'message_sid': message_sid,
                'ticket_id': ticket_id,
                'sent_via_api': not use_twiml
            }
            
        except Exception as e:
            error = str(e)
            logging.error(f"Error processing message: {error}")
            response = self.get_fallback_message()
            
            # Send fallback via API if not using TwiML
            if not use_twiml and response:
                try:
                    message_params = {
                        'body': response,
                        'to': from_number,
                        'status_callback': metadata.get('status_callback') if metadata else None
                    }
                    
                    if self.messaging_service_sid:
                        message_params['messaging_service_sid'] = self.messaging_service_sid
                    else:
                        message_params['from_'] = self.twilio_phone
                    
                    twilio_message = await self.retry_handler.retry_send(
                        message_id=None,
                        to_number=from_number,
                        from_number=self.twilio_phone,
                        body=response,
                        attempt=1,
                        metadata=metadata
                    )
                    
                    if twilio_message:
                        message_sid = twilio_message.sid
                        logging.info(f"Sent fallback message via Twilio API. SID: {message_sid}")
                except Exception as fallback_error:
                    error = f"Original error: {error}. Fallback error: {str(fallback_error)}"
                    logging.error(f"Failed to send fallback message: {error}")
        
        finally:
            # Add error to metrics if present
            if error:
                metrics['error'] = error
            
            # Record metrics
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
            ticket_id=ticket_id,
            sent_via_api=not use_twiml
        )

    def get_fallback_message(self) -> str:
        """Get the configured fallback message"""
        return self.config.get('fallback_message', 
            "We're sorry, but we couldn't process your message at this time. Please try again later."
        )

    async def process_delivery_status(
        self,
        message_sid: str,
        status: str,
        error_code: Optional[str] = None
    ):
        """Process message delivery status updates"""
        # Get message ID from database
        query = """
            SELECT id, to_number, from_number, body, metadata
            FROM sms_messages
            WHERE message_sid = :message_sid
        """
        result = await self.db.execute(query, {'message_sid': message_sid})
        message = result.fetchone()
        
        if not message:
            self.logger.error(f"Message {message_sid} not found in database")
            return
            
        if status in self.retry_handler.RETRYABLE_STATUSES:
            # Initiate retry process
            await self.retry_handler.process_failed_message(
                message_id=message.id,
                status=status,
                error_code=error_code
            )
        else:
            # Update final status
            await self.retry_handler.update_message_status(
                message_id=message.id,
                status=status,
                error_code=error_code
            )

    def _is_international(self, phone_number: str) -> bool:
        """Check if a phone number is international (non-US)"""
        return not phone_number.startswith('+1')
