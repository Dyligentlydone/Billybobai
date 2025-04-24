from typing import Dict, Optional
import os
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from pydantic import BaseModel

# Set up logging
logger = logging.getLogger(__name__)

class MessageRequest(BaseModel):
    to: str
    message: str
    type: str = "sms"  # sms, whatsapp, voice, flex
    media_url: Optional[str] = None
    ai_model: Optional[str] = None
    prompt: Optional[str] = None

class TwilioService:
    def __init__(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if account_sid and auth_token:
            self.client = Client(account_sid, auth_token)
            self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
            self.flex_flow_sid = os.getenv('TWILIO_FLEX_FLOW_SID')
        else:
            self.client = None
            self.phone_number = None
            self.flex_flow_sid = None

    def send_message(self, request: MessageRequest) -> Dict:
        """Send message via Twilio based on type (SMS, WhatsApp, Voice, or Flex)."""
        if not self.client:
            raise TwilioRestException(
                msg="Twilio credentials not configured",
                status=400,
                code=20001
            )
            
        try:
            if request.type == "sms":
                return self._send_sms(request)
            elif request.type == "whatsapp":
                return self._send_whatsapp(request)
            elif request.type == "voice":
                return self._make_call(request)
            elif request.type == "flex":
                return self._create_flex_task(request)
            else:
                raise ValueError(f"Unsupported message type: {request.type}")
        except TwilioRestException as e:
            logger.error(f"TWILIO ERROR: {str(e)}")
            error_details = {
                "code": e.code,
                "status": e.status,
                "message": str(e),
                "to": request.to,
                "from": self.phone_number
            }
            logger.error(f"TWILIO ERROR DETAILS: {error_details}")
            raise Exception(f"Twilio error: {str(e)}")
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR SENDING MESSAGE: {str(e)}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            raise Exception(f"Unexpected error: {str(e)}")

    def _send_sms(self, request: MessageRequest) -> Dict:
        """Send SMS message."""
        try:
            logger.info(f"SENDING SMS TO: {request.to}")
            logger.info(f"MESSAGE: {request.message}")
            logger.info(f"FROM NUMBER: {self.phone_number}")
            
            message = self.client.messages.create(
                to=request.to,
                from_=self.phone_number,
                body=request.message,
                media_url=[request.media_url] if request.media_url else None
            )
            
            logger.info(f"SMS SENT SUCCESSFULLY - SID: {message.sid}")
            return {
                "sid": message.sid,
                "status": message.status,
                "type": "sms"
            }
        except TwilioRestException as e:
            logger.error(f"TWILIO ERROR: {str(e)}")
            error_details = {
                "code": e.code,
                "status": e.status,
                "message": str(e),
                "to": request.to,
                "from": self.phone_number
            }
            logger.error(f"TWILIO ERROR DETAILS: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR SENDING SMS: {str(e)}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return {"error": str(e)}

    def _send_whatsapp(self, request: MessageRequest) -> Dict:
        """Send WhatsApp message."""
        try:
            logger.info(f"SENDING WHATSAPP TO: {request.to}")
            logger.info(f"MESSAGE: {request.message}")
            
            # Format WhatsApp number with proper prefix
            whatsapp_to = f"whatsapp:{request.to}"
            whatsapp_from = f"whatsapp:{self.phone_number}"
            
            message = self.client.messages.create(
                to=whatsapp_to,
                from_=whatsapp_from,
                body=request.message,
                media_url=[request.media_url] if request.media_url else None
            )
            
            logger.info(f"WHATSAPP SENT SUCCESSFULLY - SID: {message.sid}")
            return {
                "sid": message.sid,
                "status": message.status,
                "type": "whatsapp"
            }
        except TwilioRestException as e:
            logger.error(f"TWILIO ERROR: {str(e)}")
            error_details = {
                "code": e.code,
                "status": e.status,
                "message": str(e),
                "to": request.to,
                "from": self.phone_number
            }
            logger.error(f"TWILIO ERROR DETAILS: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR SENDING WHATSAPP: {str(e)}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return {"error": str(e)}

    def _make_call(self, request: MessageRequest) -> Dict:
        """Make voice call with TwiML."""
        try:
            logger.info(f"MAKING CALL TO: {request.to}")
            logger.info(f"MESSAGE: {request.message}")
            logger.info(f"FROM NUMBER: {self.phone_number}")
            
            twiml = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <Response>
                <Say>{request.message}</Say>
            </Response>
            """
            call = self.client.calls.create(
                to=request.to,
                from_=self.phone_number,
                twiml=twiml
            )
            
            logger.info(f"CALL MADE SUCCESSFULLY - SID: {call.sid}")
            return {
                "sid": call.sid,
                "status": call.status,
                "type": "voice"
            }
        except TwilioRestException as e:
            logger.error(f"TWILIO ERROR: {str(e)}")
            error_details = {
                "code": e.code,
                "status": e.status,
                "message": str(e),
                "to": request.to,
                "from": self.phone_number
            }
            logger.error(f"TWILIO ERROR DETAILS: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR MAKING CALL: {str(e)}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return {"error": str(e)}

    def _create_flex_task(self, request: MessageRequest) -> Dict:
        """Create Flex task for chat/messaging."""
        try:
            logger.info(f"CREATING FLEX TASK FOR: {request.to}")
            logger.info(f"MESSAGE: {request.message}")
            
            channel = self.client.flex.v1.channels.create(
                flex_flow_sid=self.flex_flow_sid,
                identity=request.to,
                chat_friendly_name=f"Chat with {request.to}"
            )

            # Create task for the channel
            task = self.client.taskrouter.workspaces(os.getenv('TWILIO_WORKSPACE_SID')) \
                .tasks \
                .create(
                    workflow_sid=os.getenv('TWILIO_WORKFLOW_SID'),
                    channel_sid=channel.sid,
                    attributes={
                        "type": "flex",
                        "name": request.to,
                        "message": request.message
                    }
                )

            logger.info(f"FLEX TASK CREATED SUCCESSFULLY - SID: {task.sid}")
            return {
                "sid": task.sid,
                "channel_sid": channel.sid,
                "status": task.assignment_status,
                "type": "flex"
            }
        except TwilioRestException as e:
            logger.error(f"TWILIO ERROR: {str(e)}")
            error_details = {
                "code": e.code,
                "status": e.status,
                "message": str(e),
                "to": request.to
            }
            logger.error(f"TWILIO ERROR DETAILS: {error_details}")
            return {"error": str(e), "details": error_details}
        except Exception as e:
            logger.error(f"UNEXPECTED ERROR CREATING FLEX TASK: {str(e)}")
            import traceback
            logger.error(f"TRACEBACK: {traceback.format_exc()}")
            return {"error": str(e)}

    def validate_webhook(self, request_data: Dict) -> bool:
        """Validate incoming webhook request from Twilio."""
        # Add validation logic here
        return True
