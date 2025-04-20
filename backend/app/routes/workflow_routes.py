from flask import Blueprint, request, jsonify
from app.models.workflow import Workflow
from app import db
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint without URL prefix
workflow_bp = Blueprint('workflow_bp', __name__)

@workflow_bp.route('/api/workflows', methods=['GET'])
def get_workflows():
    logger.info("GET /api/workflows endpoint called")
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
        
        workflow = Workflow(
            name=data.get('name', 'New Workflow'),
            status='draft',
            actions=data.get('actions', {}),
            conditions=data.get('conditions', {}),
            client_id=data.get('clientId'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(workflow)
        db.session.commit()
        logger.info(f"Workflow created with ID: {workflow.id}")
        
        return jsonify({
            '_id': str(workflow.id),
            'name': workflow.name,
            'status': workflow.status,
            'actions': workflow.actions,
            'conditions': workflow.conditions,
            'createdAt': workflow.created_at.isoformat(),
            'updatedAt': workflow.updated_at.isoformat()
        }), 201
    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@workflow_bp.route('/api/workflows/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    logger.info(f"PUT /api/workflows/{workflow_id} endpoint called")
    try:
        workflow = Workflow.query.get_or_404(workflow_id)
        data = request.json
        
        workflow.name = data.get('name', workflow.name)
        workflow.status = data.get('status', workflow.status)
        workflow.actions = data.get('actions', workflow.actions)
        workflow.conditions = data.get('conditions', workflow.conditions)
        workflow.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Workflow updated with ID: {workflow.id}")
        
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
