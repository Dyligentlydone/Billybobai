from flask import Blueprint, request, jsonify
from app.models.workflow import Workflow
from app import db
from datetime import datetime

workflow_bp = Blueprint('workflow_bp', __name__)

@workflow_bp.route('/api/workflows', methods=['GET'])
def get_workflows():
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
    data = request.json
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
    
    return jsonify({
        '_id': str(workflow.id),
        'name': workflow.name,
        'status': workflow.status,
        'actions': workflow.actions,
        'conditions': workflow.conditions,
        'createdAt': workflow.created_at.isoformat(),
        'updatedAt': workflow.updated_at.isoformat()
    }), 201

@workflow_bp.route('/api/workflows/<workflow_id>', methods=['PUT'])
def update_workflow(workflow_id):
    workflow = Workflow.query.get_or_404(workflow_id)
    data = request.json
    
    workflow.name = data.get('name', workflow.name)
    workflow.status = data.get('status', workflow.status)
    workflow.actions = data.get('actions', workflow.actions)
    workflow.conditions = data.get('conditions', workflow.conditions)
    workflow.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        '_id': str(workflow.id),
        'name': workflow.name,
        'status': workflow.status,
        'actions': workflow.actions,
        'conditions': workflow.conditions,
        'createdAt': workflow.created_at.isoformat(),
        'updatedAt': workflow.updated_at.isoformat()
    })

@workflow_bp.route('/api/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    workflow = Workflow.query.get_or_404(workflow_id)
    db.session.delete(workflow)
    db.session.commit()
    return '', 204

@workflow_bp.route('/api/workflows/<workflow_id>/activate', methods=['POST'])
def activate_workflow(workflow_id):
    workflow = Workflow.query.get_or_404(workflow_id)
    workflow.status = 'active'
    workflow.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        '_id': str(workflow.id),
        'name': workflow.name,
        'status': workflow.status,
        'actions': workflow.actions,
        'conditions': workflow.conditions,
        'createdAt': workflow.created_at.isoformat(),
        'updatedAt': workflow.updated_at.isoformat()
    })
