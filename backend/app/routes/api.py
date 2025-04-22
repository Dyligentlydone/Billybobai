from flask import Blueprint, request, jsonify
from ..services.twilio_service import TwilioService, MessageRequest
from ..services.sendgrid_service import SendGridService, EmailRequest, TemplatePreviewRequest
from ..services.zendesk_service import ZendeskService, TicketRequest
from ..services.ai_service import AIService
from flask_jwt_extended import jwt_required
from ..models.workflow import Workflow
from app.db import db
from ..services.workflow_engine import WorkflowEngine
from datetime import datetime
import asyncio
import os
from ..services.email_thread_service import EmailThreadService
from ..services.business_service import BusinessService
from ..models.email import InboundEmail, InboundEmailModel
from app.schemas.workflow import WorkflowConfig

api = Blueprint('api', __name__)

# Initialize services - they'll be None if credentials aren't available
twilio_service = None
sendgrid_service = None
zendesk_service = None
ai_service = None
email_thread_service = None
business_service = None

try:
    twilio_service = TwilioService()
    sendgrid_service = SendGridService()
    zendesk_service = ZendeskService()
    ai_service = AIService()
    email_thread_service = EmailThreadService()
    business_service = BusinessService()
except Exception as e:
    print(f"Warning: Some services failed to initialize: {str(e)}")

@api.route('/ai/analyze', methods=['POST'])
@jwt_required()
async def analyze_requirements():
    """Analyze requirements and generate workflow configuration."""
    try:
        data = request.get_json()
        description = data.get('description')
        if not description:
            return jsonify({"error": "Description is required"}), 400

        if ai_service is None:
            return jsonify({"error": "AI service is not available"}), 500

        workflow = await ai_service.analyze_requirements(description)
        return jsonify(workflow.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/twilio/send', methods=['POST'])
@jwt_required()
async def send_twilio_message():
    """Send message via Twilio (SMS, WhatsApp, Voice, or Flex)."""
    try:
        data = request.get_json()
        message_request = MessageRequest(**data)
        if twilio_service is None:
            return jsonify({"error": "Twilio service is not available"}), 500
        result = await twilio_service.send_message(message_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/sendgrid/send', methods=['POST'])
@jwt_required()
async def send_email():
    """Send email via SendGrid."""
    try:
        data = request.get_json()
        email_request = EmailRequest(**data)
        if sendgrid_service is None:
            return jsonify({"error": "SendGrid service is not available"}), 500
        result = await sendgrid_service.send_email(email_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/sendgrid/templates', methods=['GET'])
@jwt_required()
async def get_templates():
    """Fetch all available SendGrid templates."""
    try:
        if sendgrid_service is None:
            return jsonify({"error": "SendGrid service is not available"}), 500
        templates = await sendgrid_service.get_templates()
        return jsonify(templates), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/sendgrid/templates/preview', methods=['POST'])
@jwt_required()
async def preview_template():
    """Generate a preview of a template with test data."""
    try:
        data = request.get_json()
        preview_request = TemplatePreviewRequest(**data)
        if sendgrid_service is None:
            return jsonify({"error": "SendGrid service is not available"}), 500
        result = await sendgrid_service.preview_template(preview_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/zendesk/ticket', methods=['POST'])
@jwt_required()
async def create_ticket():
    """Create a new Zendesk ticket."""
    try:
        data = request.get_json()
        ticket_request = TicketRequest(**data)
        if zendesk_service is None:
            return jsonify({"error": "Zendesk service is not available"}), 500
        result = await zendesk_service.create_ticket(ticket_request)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/zendesk/ticket/<int:ticket_id>', methods=['PUT'])
@jwt_required()
async def update_ticket(ticket_id):
    """Update an existing Zendesk ticket."""
    try:
        data = request.get_json()
        if zendesk_service is None:
            return jsonify({"error": "Zendesk service is not available"}), 500
        result = await zendesk_service.update_ticket(ticket_id, data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/zendesk/ticket/<int:ticket_id>/comment', methods=['POST'])
@jwt_required()
async def add_ticket_comment(ticket_id):
    """Add a comment to a Zendesk ticket."""
    try:
        data = request.get_json()
        comment = data.get('comment')
        public = data.get('public', True)
        
        if not comment:
            return jsonify({"error": "Comment is required"}), 400

        if zendesk_service is None:
            return jsonify({"error": "Zendesk service is not available"}), 500
        result = await zendesk_service.add_comment(ticket_id, comment, public)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/config/email', methods=['POST'])
@jwt_required()
async def configure_email_automation():
    """Configure email automation with API keys and settings."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['sendgrid_api_key', 'sendgrid_from_email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        # Update SendGrid configuration
        os.environ['SENDGRID_API_KEY'] = data['sendgrid_api_key']
        os.environ['SENDGRID_FROM_EMAIL'] = data['sendgrid_from_email']
        
        # Optionally update Zendesk configuration
        if all(key in data for key in ['zendesk_subdomain', 'zendesk_email', 'zendesk_api_token']):
            os.environ['ZENDESK_SUBDOMAIN'] = data['zendesk_subdomain']
            os.environ['ZENDESK_EMAIL'] = data['zendesk_email']
            os.environ['ZENDESK_API_TOKEN'] = data['zendesk_api_token']
            
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows/<workflow_id>/execute', methods=['POST'])
@jwt_required()
async def execute_workflow(workflow_id):
    """Execute a workflow with the given input data."""
    try:
        # Get workflow
        workflow = Workflow.query.get_or_404(workflow_id)
        
        # Get input data from request
        input_data = request.json or {}
        
        # Initialize workflow engine
        engine = WorkflowEngine()
        
        # Execute workflow
        execution = await engine.execute_workflow(
            workflow_id=workflow_id,
            workflow_data={
                "nodes": workflow.nodes,
                "edges": workflow.edges
            },
            input_data=input_data
        )
        
        # Save execution result
        workflow.executions[str(datetime.utcnow())] = execution.dict()
        db.session.commit()
        
        return jsonify(execution.dict())
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows/<workflow_id>/executions', methods=['GET'])
@jwt_required()
async def get_workflow_executions(workflow_id):
    """Get all executions for a workflow."""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        return jsonify(workflow.executions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows/<workflow_id>/executions/<execution_id>', methods=['GET'])
@jwt_required()
async def get_workflow_execution(workflow_id, execution_id):
    """Get a specific execution for a workflow."""
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        execution = workflow.executions.get(execution_id)
        if not execution:
            return jsonify({"error": "Execution not found"}), 404
        return jsonify(execution)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route('/workflows', methods=['POST'])
def create_workflow():
    try:
        data = request.get_json()
        config = WorkflowConfig(**data)
        workflow = Workflow(
            name=data.get('name', 'Untitled Workflow'),
            status=data.get('status', 'draft'),
            business_id=data.get('business_id'),
            config=config.dict()
        )
        db.session.add(workflow)
        db.session.commit()
        return jsonify({'id': workflow.id, 'name': workflow.name, 'status': workflow.status, 'config': workflow.config}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@api.route('/workflows', methods=['GET'])
def get_workflows():
    workflows = Workflow.query.all()
    results = [
        {
            'id': w.id,
            'name': w.name,
            'status': w.status,
            'config': w.config
        } for w in workflows
    ]
    return jsonify(results)
