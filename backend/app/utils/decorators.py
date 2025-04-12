from functools import wraps
import hmac
import hashlib
import os
from flask import request, jsonify

def verify_sendgrid_webhook(f):
    """Verify that the request came from SendGrid."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not os.getenv('SENDGRID_WEBHOOK_VERIFY_KEY'):
            return jsonify({"error": "Webhook verification key not configured"}), 500

        signature = request.headers.get('X-Twilio-Email-Event-Webhook-Signature', '')
        timestamp = request.headers.get('X-Twilio-Email-Event-Webhook-Timestamp', '')
        
        if not signature or not timestamp:
            return jsonify({"error": "Missing signature headers"}), 401

        # Verify signature
        payload = timestamp + request.get_data().decode('utf-8')
        hmac_obj = hmac.new(
            key=os.getenv('SENDGRID_WEBHOOK_VERIFY_KEY').encode(),
            msg=payload.encode(),
            digestmod=hashlib.sha256
        )
        calculated_sig = hmac_obj.hexdigest()

        if not hmac.compare_digest(calculated_sig, signature):
            return jsonify({"error": "Invalid signature"}), 401

        return f(*args, **kwargs)
    return decorated_function
