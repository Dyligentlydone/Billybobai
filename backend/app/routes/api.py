from flask import Blueprint, request, jsonify
from ..services.twilio_service import TwilioService, MessageRequest
from ..services.sendgrid_service import SendGridService, EmailRequest
from ..services.zendesk_service import ZendeskService, TicketRequest
from ..services.ai_service import AIService
from flask_jwt_extended import jwt_required
from ..models import Workflow, db
from ..services.workflow_engine import WorkflowEngine
from datetime import datetime
import asyncio

api = Blueprint('api', __name__)
twilio_service = TwilioService()
sendgrid_service = SendGridService()
zendesk_service = ZendeskService()
ai_service = AIService()

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
