from flask import Blueprint, request, Response, jsonify
from services.voice_service import VoiceService
from services.ai_service import AIService
from services.config_service import ConfigService

voice_bp = Blueprint('voice', __name__)
ai_service = AIService()
voice_service = VoiceService(ai_service)
config_service = ConfigService()

@voice_bp.route('/welcome', methods=['POST'])
async def welcome():
    """Handle incoming calls with welcome message and menu."""
    # Get business phone number from Twilio request
    from_number = request.values.get('From', '')
    
    try:
        # Get voice config for this business
        config = await config_service.get_voice_config_by_phone(from_number)
        if not config:
            # Default response if no config found
            return Response(
                '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Sorry, this number is not configured for automated responses.</Say></Response>',
                mimetype='text/xml'
            )
        
        # Generate TwiML response
        twiml = voice_service.generate_welcome_twiml(config)
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in welcome: {e}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred. Please try again later.</Say></Response>',
            mimetype='text/xml'
        )

@voice_bp.route('/handle-menu', methods=['POST'])
async def handle_menu():
    """Handle menu selection."""
    from_number = request.values.get('From', '')
    digits = request.values.get('Digits', '')
    
    try:
        config = await config_service.get_voice_config_by_phone(from_number)
        if not config:
            return Response(
                '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Configuration error.</Say></Response>',
                mimetype='text/xml'
            )
        
        twiml = voice_service.handle_menu_selection(digits, config)
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in handle_menu: {e}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred. Please try again later.</Say></Response>',
            mimetype='text/xml'
        )

@voice_bp.route('/handle-input', methods=['POST'])
async def handle_input():
    """Handle voice input and generate AI response."""
    from_number = request.values.get('From', '')
    speech_result = request.values.get('SpeechResult', '')
    
    try:
        config = await config_service.get_voice_config_by_phone(from_number)
        if not config:
            return Response(
                '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Configuration error.</Say></Response>',
                mimetype='text/xml'
            )
        
        twiml = await voice_service.handle_voice_input(speech_result, config)
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in handle_input: {e}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred. Please try again later.</Say></Response>',
            mimetype='text/xml'
        )

@voice_bp.route('/handle-recording', methods=['POST'])
async def handle_recording():
    """Handle completed voicemail recording."""
    from_number = request.values.get('From', '')
    recording_url = request.values.get('RecordingUrl', '')
    
    try:
        config = await config_service.get_voice_config_by_phone(from_number)
        if not config:
            return Response(
                '<?xml version="1.0" encoding="UTF-8"?><Response><Say>Configuration error.</Say></Response>',
                mimetype='text/xml'
            )
        
        twiml = voice_service.handle_recording(recording_url, config)
        return Response(twiml, mimetype='text/xml')
        
    except Exception as e:
        print(f"Error in handle_recording: {e}")
        return Response(
            '<?xml version="1.0" encoding="UTF-8"?><Response><Say>An error occurred. Please try again later.</Say></Response>',
            mimetype='text/xml'
        )

@voice_bp.route('/config', methods=['POST'])
async def save_config():
    """Save voice configuration."""
    try:
        data = request.json
        business_id = data.get('businessId')
        config = data.get('config')
        
        if not business_id or not config:
            return jsonify({'error': 'Missing required fields'}), 400
            
        success = await config_service.save_voice_config(business_id, config)
        if success:
            return jsonify({'message': 'Voice configuration saved successfully'})
        else:
            return jsonify({'error': 'Failed to save voice configuration'}), 500
            
    except Exception as e:
        print(f"Error saving voice config: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@voice_bp.route('/config/<business_id>', methods=['GET'])
async def get_configs(business_id: str):
    """Get all voice configurations for a business."""
    try:
        configs = await config_service.get_voice_configs_by_business(business_id)
        return jsonify(configs)
            
    except Exception as e:
        print(f"Error retrieving voice configs: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@voice_bp.route('/config/<phone_number>', methods=['DELETE'])
async def delete_config(phone_number: str):
    """Delete a voice configuration."""
    try:
        success = await config_service.delete_voice_config(phone_number)
        if success:
            return jsonify({'message': 'Voice configuration deleted successfully'})
        else:
            return jsonify({'error': 'Configuration not found'}), 404
            
    except Exception as e:
        print(f"Error deleting voice config: {e}")
        return jsonify({'error': 'Internal server error'}), 500
