from flask import Blueprint, request, jsonify
from ..services.twilio_service import TwilioService, MessageRequest
from ..services.sendgrid_service import SendGridService, EmailRequest, TemplatePreviewRequest
from ..services.zendesk_service import ZendeskService, TicketRequest
from ..services.ai_service import AIService
from flask_jwt_extended import jwt_required
from ..models.workflow import Workflow
from ..database import db
from ..services.workflow_engine import WorkflowEngine
from datetime import datetime
import asyncio
import os
from functools import wraps
import hmac
import hashlib
from ..services.email_thread_service import EmailThreadService
from ..services.business_service import BusinessService
from ..models.email import InboundEmail

api = Blueprint('api', __name__)
twilio_service = TwilioService()
sendgrid_service = SendGridService()
zendesk_service = ZendeskService()
ai_service = AIService()
email_thread_service = EmailThreadService()
business_service = BusinessService()

def verify_sendgrid_webhook(f):
    """Verify that the request came from SendGrid."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get('X-Twilio-Email-Event-Webhook-Signature')
        timestamp = request.headers.get('X-Twilio-Email-Event-Webhook-Timestamp')
        
        if not signature or not timestamp:
            return jsonify({"error": "Missing signature headers"}), 401

        # Verify signature
        payload = timestamp + request.get_data(as_text=True)
        signing_key = os.environ.get('SENDGRID_SIGNING_KEY')
        
        hmac_obj = hmac.new(
            key=signing_key.encode(),
            msg=payload.encode(),
            digestmod=hashlib.sha256
        )
        
        if not hmac.compare_digest(signature, hmac_obj.hexdigest()):
            return jsonify({"error": "Invalid signature"}), 401
            
        return f(*args, **kwargs)
    return decorated_function

@api.route('/ai/analyze', methods=['POST'])
async def analyze_requirements():
    """Analyze requirements and generate workflow configuration."""
    try:
        data = request.get_json()
        description = data.get('description')
        if not description:
            return jsonify({"error": "Description is required"}), 400

        workflow = await ai_service.analyze_requirements(description)
        return jsonify(workflow.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/twilio/send', methods=['POST'])
async def send_twilio_message():
    """Send message via Twilio (SMS, WhatsApp, Voice, or Flex)."""
    try:
        data = request.get_json()
        message_request = MessageRequest(**data)
        result = await twilio_service.send_message(message_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/sendgrid/send', methods=['POST'])
async def send_email():
    """Send email via SendGrid."""
    try:
        data = request.get_json()
        email_request = EmailRequest(**data)
        result = await sendgrid_service.send_email(email_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/sendgrid/templates', methods=['GET'])
async def get_templates():
    """Fetch all available SendGrid templates."""
    try:
        templates = await sendgrid_service.get_templates()
        return jsonify(templates), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/sendgrid/templates/preview', methods=['POST'])
async def preview_template():
    """Generate a preview of a template with test data."""
    try:
        data = request.get_json()
        preview_request = TemplatePreviewRequest(**data)
        result = await sendgrid_service.preview_template(preview_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/zendesk/ticket', methods=['POST'])
async def create_ticket():
    """Create a new Zendesk ticket."""
    try:
        data = request.get_json()
        ticket_request = TicketRequest(**data)
        result = await zendesk_service.create_ticket(ticket_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/zendesk/ticket/<int:ticket_id>', methods=['PUT'])
async def update_ticket(ticket_id):
    """Update an existing Zendesk ticket."""
    try:
        data = request.get_json()
        result = await zendesk_service.update_ticket(ticket_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/zendesk/ticket/<int:ticket_id>/comment', methods=['POST'])
async def add_ticket_comment(ticket_id):
    """Add a comment to a Zendesk ticket."""
    try:
        data = request.get_json()
        comment = data.get('comment')
        public = data.get('public', True)
        
        if not comment:
            return jsonify({"error": "Comment is required"}), 400

        result = await zendesk_service.add_comment(ticket_id, comment, public)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/webhooks/sendgrid/inbound', methods=['POST'])
@verify_sendgrid_webhook
async def handle_inbound_email():
    """Handle incoming emails from SendGrid for multiple businesses."""
    try:
        data = request.get_json()
        
        # Extract business from the incoming email domain
        to_email = data.get('to', '')
        business_domain = to_email.split('@')[1] if '@' in to_email else None
        
        if not business_domain:
            return jsonify({"error": "Invalid recipient email"}), 400
            
        # Get business configuration
        business = await business_service.get_business_by_domain(business_domain)
        if not business:
            return jsonify({"error": "Business not found"}), 404
            
        # Parse incoming email with business context
        email = InboundEmail(
            business_id=business.id,
            from_email=data['from'],
            to_email=data['to'],
            subject=data['subject'],
            text=data.get('text'),
            html=data.get('html'),
            spam_score=float(data.get('spam_score', 0)),
            spam_report=data.get('spam_report', {}),
            sender_ip=data.get('sender_ip'),
            headers=data.get('headers', {}),
            envelope=data.get('envelope', {}),
            business_metadata={
                "domain": business_domain,
                "name": business.name
            }
        )

        # Get or create email thread with business context
        thread = await email_thread_service.get_or_create_thread(email)
        
        # Get conversation history
        history = await email_thread_service.get_thread_history(thread.thread_id)
        
        # Use business-specific brand voice configuration
        brand_voice = business.config.brand_voice
        
        # Generate AI response using business context
        response = await ai_service.generate_email_response(
            customer_email=email.text or email.html,
            brand_voice=brand_voice,
            conversation_history=history,
            business_context={
                "name": business.name,
                "domain": business.domain
            }
        )
        
        # Send response using business's SendGrid configuration
        if response['type'] == 'template':
            await sendgrid_service.send_email(EmailRequest(
                to=email.from_email,
                subject=f"Re: {email.subject}",
                template_id=response['template_id'],
                template_data=response['template_data'],
                type='template',
                api_key=business.config.email_config['sendgrid']['api_key'],
                from_email=business.config.email_config['sendgrid']['from_email']
            ))
        else:
            await sendgrid_service.send_email(EmailRequest(
                to=email.from_email,
                subject=f"Re: {email.subject}",
                content=response['content'],
                type='custom',
                api_key=business.config.email_config['sendgrid']['api_key'],
                from_email=business.config.email_config['sendgrid']['from_email']
            ))
        
        # Save response to thread
        await email_thread_service.add_response_to_thread(
            thread.thread_id,
            response['content'] if response['type'] == 'custom' else str(response['template_data'])
        )
        
        return jsonify({
            "status": "success",
            "thread_id": thread.thread_id,
            "business_id": business.id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/api/config/email', methods=['POST'])
async def configure_email_automation():
    """Configure email automation with API keys and settings."""
    try:
        data = request.get_json()
        
        # Update environment variables
        os.environ['SENDGRID_API_KEY'] = data['integration']['sendgridApiKey']
        os.environ['OPENAI_API_KEY'] = data['integration']['openaiApiKey']
        os.environ['SENDGRID_FROM_EMAIL'] = data['integration']['fromEmail']
        
        # Reinitialize services with new keys
        sendgrid_service.__init__()
        ai_service.__init__()
        
        return jsonify({"status": "success", "message": "Email automation configured successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows/<workflow_id>/execute', methods=['POST'])
@jwt_required
def execute_workflow(workflow_id):
    """Execute a workflow with the given input data."""
    try:
        # Get workflow
        workflow = Workflow.query.get_or_404(workflow_id)
        
        # Get input data from request
        input_data = request.json or {}
        
        # Initialize workflow engine
        engine = WorkflowEngine()
        
        # Execute workflow
        execution = asyncio.run(engine.execute_workflow(
            workflow_id=workflow_id,
            workflow_data={
                "nodes": workflow.nodes,
                "edges": workflow.edges
            },
            input_data=input_data
        ))
        
        # Save execution result
        workflow.executions[str(datetime.utcnow())] = execution.dict()
        db.session.commit()
        
        return jsonify(execution.dict())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows/<workflow_id>/executions', methods=['GET'])
@jwt_required
def get_workflow_executions(workflow_id):
    """Get all executions for a workflow."""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        return jsonify(workflow.executions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows/<workflow_id>/executions/<execution_id>', methods=['GET'])
@jwt_required
def get_workflow_execution(workflow_id, execution_id):
    """Get a specific execution for a workflow."""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        execution = workflow.executions.get(execution_id)
        if not execution:
            return jsonify({"error": "Execution not found"}), 404
        return jsonify(execution)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
