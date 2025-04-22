from flask import Blueprint, request, jsonify, current_app
from app.models.workflow import Workflow
from app.models.business import Business
from datetime import datetime
import logging
import uuid

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint without URL prefix
workflow_bp = Blueprint('workflow_bp', __name__)

def get_db():
    """Get the database session within the app context."""
    try:
        from app.database import db
        logger.info("Using db from database module")
        return db
    except ImportError:
        logger.warning("database module not found, falling back to Flask-SQLAlchemy")
        with current_app.app_context():
            from flask_sqlalchemy import SQLAlchemy
            db = SQLAlchemy(current_app)
            return db

@workflow_bp.route('/api/workflows', methods=['GET'])
def get_workflows():
    logger.info("GET /api/workflows endpoint called")
    db = get_db()
    with current_app.app_context():
        workflows = Workflow.query.all()
        return jsonify([{
            '_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
            'actions': workflow.actions,
            'conditions': workflow.conditions,
            'createdAt': workflow.created_at.isoformat(),
            'updatedAt': workflow.updated_at.isoformat()
        } for workflow in workflows])

@workflow_bp.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    logger.info(f"GET /api/workflows/{workflow_id} endpoint called")
    db = get_db()
    with current_app.app_context():
        workflow = Workflow.query.get_or_404(workflow_id)
        return jsonify({
            '_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
            'actions': workflow.actions,
            'conditions': workflow.conditions,
            'createdAt': workflow.created_at.isoformat(),
            'updatedAt': workflow.updated_at.isoformat()
        })

@workflow_bp.route('/api/workflows', methods=['POST'])
def create_workflow():
    logger.info("POST /api/workflows endpoint called")
    try:
        data = request.json
        logger.info(f"Received workflow data: {data}")
        logger.info(f"Attempting to save SMS configuration from SMSConfigWizard")
        
        # Validate required fields for SMS workflow
        if data.get('workflow_type') == 'sms_automation':
            config = data.get('config', {})
            twilio_config = config.get('twilio', {})
            if not twilio_config or 'accountSid' not in twilio_config or 'authToken' not in twilio_config:
                logger.error("Missing required Twilio configuration for SMS workflow")
                return jsonify({"error": "Missing required Twilio configuration for SMS workflow"}), 400
        
        # Generate a UUID for the workflow
        workflow_id = str(uuid.uuid4())
        
        # Extract data from the request, specifically handling SMS configurations
        config = data.get('config', {})
        twilio_config = config.get('twilio', {})
        actions = data.get('actions', {})
        if not actions and config:
            # Structure actions based on SMSConfigWizard data
            actions = {
                'twilio': twilio_config,
                'brandTone': config.get('brandTone', {}),
                'aiTraining': config.get('aiTraining', {}),
                'context': config.get('context', {}),
                'response': config.get('response', {}),
                'monitoring': config.get('monitoring', {}),
                'systemIntegration': config.get('systemIntegration', {})
            }
        
        status = data.get('status', 'DRAFT')
        status = status.upper() if isinstance(status, str) else 'DRAFT'
        
        # Ensure the business exists before creating the workflow
        db = get_db()
        with current_app.app_context():
            business_id = data.get('business_id')
            # Ensure business_id is an integer
            if business_id is not None:
                try:
                    business_id = int(business_id)
                    # Convert back to string since database expects VARCHAR
                    business_id = str(business_id)
                    existing_business = Business.query.filter_by(id=business_id).first()
                    if not existing_business:
                        # Use a default name if not provided
                        business_name = data.get('business_name', f'Business {business_id}')
                        new_business = Business(id=business_id, name=business_name)
                        db.session.add(new_business)
                        db.session.commit()
                except (ValueError, TypeError):
                    logger.error(f"Invalid business_id format: {business_id}. Must be a valid integer.")
                    return jsonify({"error": "Business ID must be a valid integer"}), 400
        
        workflow = Workflow(
            id=workflow_id,
            name=data.get('name', 'SMS Automation Workflow'),
            status=status,
            actions=actions,
            conditions=data.get('conditions', {}),
            business_id=business_id,  # Use the already validated business_id 
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Log the workflow object before adding to session
        logger.info(f"Created workflow object: {workflow}")
        
        db = get_db()
        with current_app.app_context():
            try:
                db.session.add(workflow)
                db.session.commit()
                logger.info(f"Workflow created with ID: {workflow.id}")
                logger.info(f"SMS configuration successfully saved for workflow ID: {workflow.id}")
                
                return jsonify({
                    '_id': str(workflow.id),
                    'name': workflow.name,
                    'status': workflow.status,
                    'actions': workflow.actions,
                    'conditions': workflow.conditions,
                    'createdAt': workflow.created_at.isoformat(),
                    'updatedAt': workflow.updated_at.isoformat()
                }), 201
            except Exception as db_error:
                logger.error(f"Database error while saving workflow: {str(db_error)}")
                import traceback
                logger.error(traceback.format_exc())
                db.session.rollback()
                return jsonify({"error": str(db_error)}), 500
                
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@workflow_bp.route('/api/workflows/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    logger.info(f"PUT /api/workflows/{workflow_id} endpoint called")
    try:
        db = get_db()
        with current_app.app_context():
            workflow = Workflow.query.get_or_404(workflow_id)
            data = request.json
            logger.info(f"Received update data for workflow {workflow_id}: {data}")
            logger.info(f"Attempting to update SMS configuration for workflow ID: {workflow_id}")
            
            workflow.name = data.get('name', workflow.name)
            workflow.status = data.get('status', workflow.status)
            
            # Handle SMS configuration updates
            config = data.get('config', {})
            if config:
                twilio_config = config.get('twilio', {})
                actions = data.get('actions', {})
                if not actions:
                    actions = {
                        'twilio': twilio_config,
                        'brandTone': config.get('brandTone', {}),
                        'aiTraining': config.get('aiTraining', {}),
                        'context': config.get('context', {}),
                        'response': config.get('response', {}),
                        'monitoring': config.get('monitoring', {}),
                        'systemIntegration': config.get('systemIntegration', {})
                    }
                workflow.actions = actions
            else:
                workflow.actions = data.get('actions', workflow.actions)
            
            workflow.conditions = data.get('conditions', workflow.conditions)
            workflow.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"Workflow updated with ID: {workflow.id}")
            logger.info(f"SMS configuration successfully updated for workflow ID: {workflow.id}")
            
            return jsonify({
                '_id': str(workflow.id),
                'name': workflow.name,
                'status': workflow.status,
                'actions': workflow.actions,
                'conditions': workflow.conditions,
                'createdAt': workflow.created_at.isoformat(),
                'updatedAt': workflow.updated_at.isoformat()
            })
    except Exception as e:
        logger.error(f"Error updating workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@workflow_bp.route('/api/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    logger.info(f"DELETE /api/workflows/{workflow_id} endpoint called")
    try:
        db = get_db()
        with current_app.app_context():
            workflow = Workflow.query.get_or_404(workflow_id)
            db.session.delete(workflow)
            db.session.commit()
            logger.info(f"Workflow deleted with ID: {workflow_id}")
            return '', 204
    except Exception as e:
        logger.error(f"Error deleting workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@workflow_bp.route('/api/workflows/<workflow_id>/activate', methods=['POST'])
def activate_workflow(workflow_id):
    logger.info(f"POST /api/workflows/{workflow_id}/activate endpoint called")
    try:
        db = get_db()
        with current_app.app_context():
            workflow = Workflow.query.get_or_404(workflow_id)
            workflow.status = 'active'
            workflow.updated_at = datetime.utcnow()
            db.session.commit()
            logger.info(f"Workflow activated with ID: {workflow_id}")
            
            return jsonify({
                '_id': str(workflow.id),
                'name': workflow.name,
                'status': workflow.status,
                'actions': workflow.actions,
                'conditions': workflow.conditions,
                'createdAt': workflow.created_at.isoformat(),
                'updatedAt': workflow.updated_at.isoformat()
            })
    except Exception as e:
        logger.error(f"Error activating workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
