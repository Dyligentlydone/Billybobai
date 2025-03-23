from flask import Blueprint, request, jsonify
from services.monitoring import MonitoringService
from typing import Dict, Optional, Any
import logging

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
def record_message_metrics(
    business_id: str,
    workflow_id: str,
    workflow_name: str,
    thresholds: Dict[str, Any],
    metrics: Dict[str, Any]
) -> None:
    """Record message processing metrics"""
    try:
        # Log metrics
        logging.info(f"Message metrics for {workflow_name} ({workflow_id}):")
        logging.info(f"Business ID: {business_id}")
        logging.info("Metrics:")
        for key, value in metrics.items():
            logging.info(f"  {key}: {value}")
        
        # Check thresholds
        if 'response_time' in metrics and metrics['response_time'] > thresholds.get('response_time', 5000):
            logging.warning(f"Response time ({metrics['response_time']}ms) exceeded threshold")
            
        if 'ai_time' in metrics and metrics['ai_time'] > thresholds.get('ai_time', 3000):
            logging.warning(f"AI processing time ({metrics['ai_time']}ms) exceeded threshold")
            
        if 'error' in metrics:
            logging.error(f"Error in message processing: {metrics['error']}")
            
    except Exception as e:
        logging.error(f"Error recording metrics: {str(e)}")
        # Don't raise the error - we don't want metrics recording to break message processing
