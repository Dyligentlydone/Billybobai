from typing import Dict, Optional
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from pydantic import BaseModel

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

    async def send_message(self, request: MessageRequest) -> Dict:
        """Send message via Twilio based on type (SMS, WhatsApp, Voice, or Flex)."""
        if not self.client:
            raise TwilioRestException(
                msg="Twilio credentials not configured",
                status=400,
                code=20001
            )
            
        try:
            if request.type == "sms":
                return await self._send_sms(request)
            elif request.type == "whatsapp":
                return await self._send_whatsapp(request)
            elif request.type == "voice":
                return await self._make_call(request)
            elif request.type == "flex":
                return await self._create_flex_task(request)
            else:
                raise ValueError(f"Unsupported message type: {request.type}")
        except TwilioRestException as e:
            raise Exception(f"Twilio error: {str(e)}")

    async def _send_sms(self, request: MessageRequest) -> Dict:
        """Send SMS message."""
        message = await self.client.messages.create(
            to=request.to,
            from_=self.phone_number,
            body=request.message,
            media_url=[request.media_url] if request.media_url else None
        )
        return {
            "sid": message.sid,
            "status": message.status,
            "type": "sms"
        }

    async def _send_whatsapp(self, request: MessageRequest) -> Dict:
        """Send WhatsApp message."""
        message = await self.client.messages.create(
            to=f"whatsapp:{request.to}",
            from_=f"whatsapp:{self.phone_number}",
            body=request.message,
            media_url=[request.media_url] if request.media_url else None
        )
        return {
            "sid": message.sid,
            "status": message.status,
            "type": "whatsapp"
        }

    async def _make_call(self, request: MessageRequest) -> Dict:
        """Make voice call with TwiML."""
        twiml = f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <Say>{request.message}</Say>
        </Response>
        """
        call = await self.client.calls.create(
            to=request.to,
            from_=self.phone_number,
            twiml=twiml
        )
        return {
            "sid": call.sid,
            "status": call.status,
            "type": "voice"
        }

    async def _create_flex_task(self, request: MessageRequest) -> Dict:
        """Create Flex task for chat/messaging."""
        channel = await self.client.flex.v1.channels.create(
            flex_flow_sid=self.flex_flow_sid,
            identity=request.to,
            chat_friendly_name=f"Chat with {request.to}"
        )

        # Create task for the channel
        task = await self.client.taskrouter.workspaces(os.getenv('TWILIO_WORKSPACE_SID')) \
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

        return {
            "sid": task.sid,
            "channel_sid": channel.sid,
            "status": task.assignment_status,
            "type": "flex"
        }

    def validate_webhook(self, request_data: Dict) -> bool:
        """Validate incoming webhook request from Twilio."""
        # Add validation logic here
        return True
