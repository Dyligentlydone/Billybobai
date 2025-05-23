from flask import Blueprint, request, jsonify, current_app
from app.models.workflow import Workflow, WorkflowStatus
from app.models.business import Business
from datetime import datetime
import logging
import uuid
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint without URL prefix
workflow_bp = Blueprint('workflow_bp', __name__)

# Admin password for authentication
ADMIN_PASSWORD = "97225"

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

def check_admin_auth():
    """Check if the request has admin authentication"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        logger.warning("No Authorization header provided")
        return False
    
    try:
        # Handle both Basic and Bearer auth formats
        if auth_header.startswith('Basic '):
            encoded = auth_header.split(' ')[1]
            decoded = base64.b64decode(encoded).decode('utf-8')
            # Simple check - if the admin password is in the decoded string
            if ADMIN_PASSWORD in decoded:
                logger.info("Admin authentication successful")
                return True
        elif auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # For Bearer tokens, we just check if it matches the admin password
            if token == ADMIN_PASSWORD:
                logger.info("Admin authentication with Bearer successful")
                return True
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
    
    logger.warning("Authentication failed")
    return False

@workflow_bp.route('/api/workflows', methods=['GET'])
def get_workflows():
    logger.info("GET /api/workflows endpoint called")
    try:
        # Log headers for debugging
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Check admin authentication
        is_admin = check_admin_auth()
        logger.info(f"Admin authentication: {is_admin}")
        
        db = get_db()
        with current_app.app_context():
            try:
                # Check if we can actually query the database
                from sqlalchemy import text
                test_result = db.session.execute(text("SELECT 1")).fetchone()
                logger.info(f"Database connection test: {test_result}")
                
                # List all tables to verify schema
                inspector = db.inspect(db.engine)
                all_tables = inspector.get_table_names()
                logger.info(f"Database tables: {all_tables}")
                
                # If admin, show all workflows, otherwise filter by business
                if is_admin:
                    logger.info("Admin access: fetching all workflows")
                    workflows = Workflow.query.all()
                else:
                    # Non-admin access is limited by business_id
                    business_id = request.args.get('business_id')
                    if not business_id:
                        logger.warning("No business_id provided for non-admin request")
                        return jsonify([])
                    
                    logger.info(f"Fetching workflows for business_id: {business_id}")
                    workflows = Workflow.query.filter_by(business_id=business_id).all()
                
                logger.info(f"Found {len(workflows)} workflows")
                
                # Return empty list instead of 404 if no workflows found
                return jsonify([{
                    '_id': str(workflow.id),
                    'name': workflow.name,
                    'status': workflow.status,
                    'actions': workflow.actions,
                    'conditions': workflow.conditions,
                    'createdAt': workflow.created_at.isoformat(),
                    'updatedAt': workflow.updated_at.isoformat()
                } for workflow in workflows])
            except Exception as e:
                logger.error(f"Error querying workflows: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                # Return empty array on error to prevent frontend breakage
                return jsonify([])
    except Exception as e:
        logger.error(f"Error in get_workflows route: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        # Return empty array on error to prevent frontend breakage
        return jsonify([])

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
        
        # Normalize phone number field - this handles the field name mismatch
        if 'phoneNumber' in twilio_config and 'twilioPhoneNumber' not in twilio_config:
            twilio_config['twilioPhoneNumber'] = twilio_config['phoneNumber']
            
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
            # Accept any business_id format and convert to string
            if business_id is not None:
                # Always convert to string for database operations
                business_id_str = str(business_id)
                existing_business = Business.query.filter_by(id=business_id_str).first()
                if not existing_business:
                    # Use a default name if not provided
                    business_name = data.get('business_name', f'Business {business_id}')
                    # Create new business with ID as string
                    new_business = Business(
                        id=business_id_str,  # Use string ID for database
                        name=business_name,
                        description="Created automatically by SMSConfigWizard",
                        domain=f"business-{business_id}.com"
                    )
                    db.session.add(new_business)
                    db.session.commit()
                    logger.info(f"Created new business with ID: {business_id_str} and name: {business_name}")
        
        workflow = Workflow(
            id=workflow_id,
            name=data.get('name', 'SMS Automation Workflow'),
            status=status,
            actions=actions,
            conditions=data.get('conditions', {}),
            business_id=str(data.get('business_id')),  # Use string business ID for database
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
                
                # Normalize phone number field in update function too
                if 'phoneNumber' in twilio_config and 'twilioPhoneNumber' not in twilio_config:
                    twilio_config['twilioPhoneNumber'] = twilio_config['phoneNumber']
                
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
            
            # Use the enum value from the WorkflowStatus class instead of a string literal
            from app.models.workflow import WorkflowStatus
            workflow.status = WorkflowStatus.ACTIVE
            
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
