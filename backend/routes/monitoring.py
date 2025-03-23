from flask import Blueprint, request, jsonify
from services.monitoring import MonitoringService
from typing import Dict

# Global monitoring service instance
monitor: Dict[str, MonitoringService] = {}

bp = Blueprint('monitoring', __name__)

@bp.route('/api/monitoring/config', methods=['POST'])
def update_config():
    """Update monitoring configuration for a workflow"""
    data = request.json
    workflow_id = data.get('workflowId')
    config = data.get('config', {})
    
    if not workflow_id:
        return jsonify({'error': 'workflowId is required'}), 400
        
    # Create or update monitoring service for this workflow
    if workflow_id not in monitor:
        monitor[workflow_id] = MonitoringService(config)
    else:
        monitor[workflow_id].update_config(config)
        
    return jsonify({'status': 'success'})

@bp.route('/api/monitoring/metrics/<workflow_id>', methods=['GET'])
def get_metrics(workflow_id):
    """Get current metrics for a workflow"""
    if workflow_id not in monitor:
        return jsonify({'error': 'Monitoring not configured for this workflow'}), 404
        
    return jsonify(monitor[workflow_id].get_metrics())

@bp.route('/api/monitoring/test/<workflow_id>', methods=['POST'])
def test_alerts(workflow_id):
    """Test Slack alerts configuration"""
    if workflow_id not in monitor or not monitor[workflow_id].alerter:
        return jsonify({'error': 'Slack alerts not configured for this workflow'}), 404
        
    success = monitor[workflow_id].alerter.test_connection()
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to send test alert'}), 500

# These functions should be called from your message processing logic
def record_response_time(workflow_id: str, response_time: int):
    """Record response time for monitoring"""
    if workflow_id in monitor:
        monitor[workflow_id].record_response_time(response_time)

def record_error(workflow_id: str, error: str):
    """Record an error for monitoring"""
    if workflow_id in monitor:
        monitor[workflow_id].record_error(error)

def record_message(workflow_id: str):
    """Record a message for volume monitoring"""
    if workflow_id in monitor:
        monitor[workflow_id].record_message()
