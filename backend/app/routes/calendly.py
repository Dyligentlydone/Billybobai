from flask import Blueprint, request, jsonify
from ..services.calendly import CalendlyService
from ..schemas.calendly import CalendlyConfig, BookingRequest, WebhookEvent, SMSNotificationSettings
from ..models import Business
from sqlalchemy.orm import Session
from typing import Optional
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('calendly', __name__)

def get_calendly_service(business_id: int, db: Session) -> Optional[CalendlyService]:
    """Get Calendly service instance for a business"""
    business = db.query(Business).get(business_id)
    if not business or not business.config or not business.config.calendly_settings:
        return None
    
    config = CalendlyConfig(**business.config.calendly_settings)
    return CalendlyService(config)

@bp.route('/api/calendly/setup-sms', methods=['POST'])
async def setup_sms_workflow():
    """Set up or update Calendly SMS workflow"""
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        # Get SMS notification settings from request
        settings = SMSNotificationSettings(**request.json)
        
        # Update service config with new settings
        service.config.sms_notifications = settings
        
        # Set up the workflow
        workflow = await service.setup_sms_workflow()
        return jsonify(workflow)
    except Exception as e:
        logger.error(f"Error setting up SMS workflow: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calendly/event-types', methods=['GET'])
async def get_event_types():
    """Get available event types for the business"""
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        event_types = await service.get_event_types()
        return jsonify(event_types)
    except Exception as e:
        logger.error(f"Error fetching event types: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calendly/test-connection', methods=['POST'])
async def test_connection():
    """Test Calendly API connection"""
    try:
        data = request.json
        config = CalendlyConfig(**data)
        service = CalendlyService(config)
        
        # Try to fetch event types as a connection test
        await service.get_event_types()
        
        # If SMS notifications are enabled, test workflow setup
        if config.sms_notifications.enabled:
            await service.setup_sms_workflow()
            
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calendly/available-slots', methods=['GET'])
async def get_available_slots():
    """Get available time slots for an event type"""
    try:
        business_id = request.args.get('business_id', type=int)
        event_type_id = request.args.get('event_type_id')
        if not business_id or not event_type_id:
            return jsonify({"error": "business_id and event_type_id are required"}), 400

        service = get_calendly_service(business_id)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        slots = await service.get_available_slots(event_type_id)
        return jsonify(slots)
    except Exception as e:
        logger.error(f"Error fetching available slots: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calendly/book', methods=['POST'])
async def create_booking():
    """Create a new booking"""
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        booking_request = BookingRequest(**request.json)
        booking = await service.create_booking(booking_request)
        return jsonify(booking)
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/calendly/webhook', methods=['POST'])
async def handle_webhook():
    """Handle Calendly webhook events"""
    try:
        event = WebhookEvent(**request.json)
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        # We don't need to do anything with webhooks anymore since Calendly handles SMS
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500
