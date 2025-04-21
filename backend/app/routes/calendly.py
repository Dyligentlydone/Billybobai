from flask import Blueprint, request, jsonify
from ..services.calendly import CalendlyService
from ..schemas.calendly import CalendlyConfig, BookingRequest, WebhookEvent, SMSNotificationSettings as SMSSchema
from ..models import Business
from app.db import get_session
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
bp = Blueprint('calendly', __name__)

def get_db():
    db = get_session()
    try:
        yield db
    finally:
        db.close()

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
    db = next(get_db())
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id, db)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        # Get SMS notification settings from request
        settings = SMSSchema(**request.json)
        
        # Update business config with new settings
        business = db.query(Business).get(business_id)
        if not business.config:
            return jsonify({"error": "Business configuration not found"}), 404
            
        business.config.calendly_settings['sms_notifications'] = settings.dict()
        db.commit()
        
        # Set up the workflow
        workflow = await service.setup_sms_workflow()
        
        # Update workflow ID in settings if provided
        if workflow and workflow.get('id'):
            business.config.calendly_settings['sms_workflow_id'] = workflow['id']
            db.commit()
            
        return jsonify(workflow)
    except Exception as e:
        db.rollback()
        logger.error(f"Error setting up SMS workflow: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@bp.route('/api/calendly/event-types', methods=['GET'])
async def get_event_types():
    """Get available event types for the business"""
    db = next(get_db())
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id, db)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        event_types = await service.get_event_types()
        return jsonify(event_types)
    except Exception as e:
        logger.error(f"Error getting event types: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@bp.route('/api/calendly/test-connection', methods=['GET'])
async def test_connection():
    """Test Calendly API connection"""
    db = next(get_db())
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id, db)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        result = await service.test_connection()
        return jsonify({"success": result})
    except Exception as e:
        logger.error(f"Error testing connection: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@bp.route('/api/calendly/available-slots', methods=['GET'])
async def get_available_slots():
    """Get available time slots for an event type"""
    db = next(get_db())
    try:
        business_id = request.args.get('business_id', type=int)
        event_type_id = request.args.get('event_type_id')
        if not business_id or not event_type_id:
            return jsonify({"error": "business_id and event_type_id are required"}), 400

        service = get_calendly_service(business_id, db)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        slots = await service.get_available_slots(event_type_id)
        return jsonify(slots)
    except Exception as e:
        logger.error(f"Error fetching available slots: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@bp.route('/api/calendly/book', methods=['POST'])
async def create_booking():
    """Create a new booking"""
    db = next(get_db())
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id, db)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        booking_request = BookingRequest(**request.json)
        booking = await service.create_booking(booking_request)
        return jsonify(booking)
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

@bp.route('/api/calendly/webhook', methods=['POST'])
async def handle_webhook():
    """Handle Calendly webhook events"""
    db = next(get_db())
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
    finally:
        db.close()

@bp.route('/api/calendly/test-sms', methods=['POST'])
async def test_sms():
    """Test SMS notification templates"""
    db = next(get_db())
    try:
        business_id = request.args.get('business_id', type=int)
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400

        service = get_calendly_service(business_id, db)
        if not service:
            return jsonify({"error": "Calendly not configured"}), 404

        # Get the business's phone number for testing
        business = db.query(Business).get(business_id)
        if not business or not business.phone:
            return jsonify({"error": "Business phone number not configured"}), 404

        # Send test messages
        settings = business.config.calendly_settings.get('sms_notifications', {})
        if not settings.get('enabled'):
            return jsonify({"error": "SMS notifications are not enabled"}), 400

        # Replace variables in messages
        test_time = datetime.now() + timedelta(days=1)
        time_str = test_time.strftime("%B %d at %I:%M %p")
        
        messages = {
            'confirmation': settings['confirmation_message'].replace('{{time}}', time_str),
            'reminder': settings['reminder_message'].replace('{{time}}', time_str),
            'cancellation': settings['cancellation_message'].replace('{{time}}', time_str),
            'reschedule': settings['reschedule_message'].replace('{{time}}', time_str)
        }

        # Send test message using Twilio service
        from ..services.twilio import send_sms
        for msg_type, message in messages.items():
            await send_sms(
                to=business.phone,
                message=f"TEST - {msg_type.upper()}: {message}"
            )

        return jsonify({"success": True, "message": "Test SMS messages sent"})
    except Exception as e:
        logger.error(f"Error sending test SMS: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
