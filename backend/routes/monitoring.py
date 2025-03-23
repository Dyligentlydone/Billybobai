from flask import Blueprint, request, jsonify
from services.monitoring import MonitoringService
from typing import Dict, Optional

# Global monitoring service instance
monitor = MonitoringService()

bp = Blueprint('monitoring', __name__)

@bp.route('/api/monitoring/config', methods=['POST'])
def update_config():
    """Update monitoring configuration for a business workflow"""
    data = request.json
    business_id = data.get('businessId')
    config = data.get('config', {})
    
    if not business_id:
        return jsonify({'error': 'businessId is required'}), 400
        
    # Configure monitoring for this business
    monitor.configure_business(business_id, config)
    return jsonify({'status': 'success'})

@bp.route('/api/monitoring/metrics/workflow/<business_id>/<workflow_id>', methods=['GET'])
def get_workflow_metrics(business_id, workflow_id):
    """Get current metrics for a specific workflow"""
    metrics = monitor.get_workflow_metrics(business_id, workflow_id)
    return jsonify(metrics)

@bp.route('/api/monitoring/metrics/business/<business_id>', methods=['GET'])
def get_business_metrics(business_id):
    """Get aggregated metrics for an entire business"""
    metrics = monitor.get_business_metrics(business_id)
    return jsonify(metrics)

@bp.route('/api/monitoring/test', methods=['POST'])
def test_alerts():
    """Test Slack alerts configuration"""
    data = request.json
    business_id = data.get('businessId')
    config = data.get('config', {})
    
    if not business_id:
        return jsonify({'error': 'businessId is required'}), 400
        
    # Configure temporarily for testing
    monitor.configure_business(business_id, config)
    success = monitor.test_connection()
    if success:
        return jsonify({'status': 'success'})
    return jsonify({'error': 'Failed to send test alert'}), 500

# These functions should be called from your message processing logic
def record_message_metrics(business_id: str, workflow_id: str, workflow_name: str, 
                         response_time: int, error: Optional[str], thresholds: Dict):
    """Record all metrics for a message"""
    # Record the message
    monitor.record_message(business_id, workflow_id, workflow_name, thresholds)
    
    # Record response time
    monitor.record_response_time(business_id, workflow_id, workflow_name, response_time, thresholds)
    
    # Record error if present
    if error:
        monitor.record_error(business_id, workflow_id, workflow_name, error, thresholds)
