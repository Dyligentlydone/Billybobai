from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from ..database import get_db
import re

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

@router.post("/twilio/webhook")
def twilio_webhook(request: Request, db: Session = Depends(get_db)):
    # Implement Twilio webhook logic
    return {"detail": "Twilio webhook received (mock)"}

@router.post("/sendgrid/webhook")
def sendgrid_webhook(request: Request, db: Session = Depends(get_db)):
    # Implement Sendgrid webhook logic
    return {"detail": "Sendgrid webhook received (mock)"}

@router.post("/zendesk/webhook")
def zendesk_webhook(request: Request, db: Session = Depends(get_db)):
    # Implement Zendesk webhook logic
    return {"detail": "Zendesk webhook received (mock)"}

from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.models.business import Business
from app.models.workflow import Workflow
from app.models.sms_consent import SMSConsent
from app.models.message import Message, MessageDirection, MessageChannel, MessageStatus
from config.database import SessionLocal
import logging
from datetime import datetime
import uuid

@router.api_route("/sms/webhook/{business_id}", methods=["GET", "POST"])
async def sms_webhook(business_id: str, request: Request, db: Session = Depends(get_db)):
    logger = logging.getLogger(__name__)
    resp = MessagingResponse()
    try:
        form = {}
        if request.method == "POST":
            form = dict((await request.form()).items())
        elif request.method == "GET":
            form = dict(request.query_params)
        from_number = form.get('From', 'unknown')
        body = form.get('Body', '')
        logger.info(f"SMS WEBHOOK: business_id={business_id}, from={from_number}, body={body}")
        # Business lookup
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            resp.message(f"Thank you for your message. We'll get back to you soon. (Business ID: {business_id} not found)")
            return Response(content=str(resp), media_type="application/xml")
        # Workflow lookup
        workflow = db.query(Workflow).filter(Workflow.business_id == business_id, Workflow.is_active == True).first()
        if not workflow:
            resp.message("Thank you for your message. A representative will get back to you soon. (No active workflow)")
            return Response(content=str(resp), media_type="application/xml")
        # Consent
        consent_record = db.query(SMSConsent).filter(SMSConsent.phone_number == from_number, SMSConsent.business_id == business_id).first()
        if not consent_record:
            new_consent = SMSConsent(phone_number=from_number, business_id=business_id, status='PENDING')
            db.add(new_consent)
            db.commit()
            consent_record = new_consent
        body_upper = body.strip().upper() if body else ''
        if body_upper == 'YES':
            if consent_record.status != 'CONFIRMED':
                consent_record.status = 'CONFIRMED'
                db.commit()
            resp.message("Thanks! You've opted in to receive SMS updates. Reply STOP to opt out anytime.")
            return Response(content=str(resp), media_type="application/xml")
        if body_upper == 'STOP':
            if consent_record.status != 'DECLINED':
                consent_record.status = 'DECLINED'
                db.commit()
            resp.message("You have been opted out and will no longer receive automated SMS. Reply YES to opt back in.")
            return Response(content=str(resp), media_type="application/xml")
        if consent_record.status == 'DECLINED':
            resp.message("You are currently opted out of SMS messages. Reply YES to opt back in.")
            return Response(content=str(resp), media_type="application/xml")
        include_opt_in_prompt = consent_record.status == 'PENDING'
        # AI Service
        from app.services.ai_service import AIService
        ai_service = AIService()
        logger.info(f"AI DEBUG: Sending user message to AI: body='{body}'")
        if not body or not body.strip():
            logger.warning("AI DEBUG: User message (body) is empty. Skipping AI call and using fallback.")
            ai_response_text = workflow.actions.get('twilio', {}).get('fallbackMessage') or workflow.actions.get('response', {}).get('fallbackMessage') or "Thank you for your message. We'll respond shortly."
            workflow_response = {'message': ai_response_text}
        else:
            # Conversation history
            recent_messages = db.query(Message).filter(Message.phone_number == from_number, Message.workflow_id == workflow.id).order_by(Message.created_at.desc()).limit(10).all()
            is_first_message = len(recent_messages) == 0
            conversation_timeout_minutes = workflow.actions.get('response', {}).get('conversationTimeoutMinutes', 30)
            is_new_conversation = is_first_message
            current_conversation_id = None
            if not is_first_message:
                last_message_time = recent_messages[0].created_at
                time_difference = (datetime.utcnow() - last_message_time).total_seconds() / 60
                is_new_conversation = time_difference > conversation_timeout_minutes
                if not is_new_conversation and recent_messages[0].conversation_id:
                    current_conversation_id = recent_messages[0].conversation_id
            if is_new_conversation or not current_conversation_id:
                current_conversation_id = str(uuid.uuid4())
            # Store incoming message
            session = SessionLocal()
            try:
                incoming_message = Message(
                    workflow_id=workflow.id,
                    direction=MessageDirection.INBOUND,
                    channel=MessageChannel.SMS,
                    content=body,
                    phone_number=from_number,
                    conversation_id=current_conversation_id,
                    status=MessageStatus.RECEIVED
                )
                session.add(incoming_message)
                session.commit()
                incoming_message_id = incoming_message.id
            except Exception as db_error:
                logger.error(f"Error storing incoming message: {str(db_error)}")
                session.rollback()
                incoming_message_id = None
            finally:
                session.close()

            # Build conversation history for AI
            conversation_history = []
            for msg in reversed(recent_messages):
                if msg.direction == MessageDirection.INBOUND:
                    conversation_history.append({"role": "user", "content": msg.content})
                else:
                    conversation_history.append({"role": "assistant", "content": msg.content})
            conversation_history.append({"role": "user", "content": body})

            logger.info(f"AI DEBUG: Prepared conversation_history for AI: {conversation_history}")

            # Call AI service
            workflow_response = ai_service.analyze_requirements(
                body,
                workflow.actions,
                conversation_history=conversation_history,
                is_new_conversation=is_new_conversation
            )
            ai_response_text = workflow_response.get('message', '')
            # (rest of the original logic continues here)
        # Conversation history
        recent_messages = db.query(Message).filter(Message.phone_number == from_number, Message.workflow_id == workflow.id).order_by(Message.created_at.desc()).limit(10).all()
        is_first_message = len(recent_messages) == 0
        conversation_timeout_minutes = workflow.actions.get('response', {}).get('conversationTimeoutMinutes', 30)
        is_new_conversation = is_first_message
        current_conversation_id = None
        if not is_first_message:
            last_message_time = recent_messages[0].created_at
            time_difference = (datetime.utcnow() - last_message_time).total_seconds() / 60
            is_new_conversation = time_difference > conversation_timeout_minutes
            if not is_new_conversation and recent_messages[0].conversation_id:
                current_conversation_id = recent_messages[0].conversation_id
        if is_new_conversation or not current_conversation_id:
            current_conversation_id = str(uuid.uuid4())
        # Store incoming message
        session = SessionLocal()
        try:
            incoming_message = Message(
                workflow_id=workflow.id,
                direction=MessageDirection.INBOUND,
                channel=MessageChannel.SMS,
                content=body,
                phone_number=from_number,
                conversation_id=current_conversation_id,
                is_first_in_conversation=is_new_conversation,
                status=MessageStatus.DELIVERED
            )
            session.add(incoming_message)
            session.commit()
            incoming_message_id = incoming_message.id
        except Exception as db_error:
            logger.error(f"Error storing incoming message: {str(db_error)}")
            session.rollback()
            incoming_message_id = None
        finally:
            session.close()
        # Prepare conversation history for AI
        conversation_history = []
        if not is_new_conversation and len(recent_messages) > 0:
            for msg in recent_messages[:5]:
                conversation_history.append({
                    "role": "user" if msg.direction == MessageDirection.INBOUND else "assistant",
                    "content": msg.content
                })
            conversation_history.reverse()
        # AI response
        workflow_response = ai_service.analyze_requirements(body, workflow.actions, conversation_history=conversation_history, is_new_conversation=is_new_conversation)
        ai_response_text = workflow_response.get('message', '')
        if not ai_response_text:
            import json
            # Try to extract from stringified JSON or fallback to string
            try:
                if isinstance(workflow_response, str):
                    try:
                        parsed = json.loads(workflow_response)
                        ai_response_text = parsed.get('message', '')
                    except Exception:
                        ai_response_text = workflow_response
                elif isinstance(workflow_response, dict):
                    # Try to find any non-empty string value
                    for v in workflow_response.values():
                        if isinstance(v, str) and v.strip():
                            ai_response_text = v
                            break
                if not ai_response_text:
                    logger.error(f"AI response extraction failed. Full response: {workflow_response}")
            except Exception as err:
                logger.error(f"AI response extraction error: {err}, full response: {workflow_response}")
        include_next_steps = workflow_response.get('include_next_steps', False)
        include_sign_off = workflow_response.get('include_sign_off', False)
        # Template/message structure
        response_text = ""
        message_structure = workflow.actions.get('response', {}).get('messageStructure', [])
        if message_structure and isinstance(message_structure, list):
            for section in message_structure:
                if section.get('enabled', True):
                    section_name = section.get('name', '').lower()
                    section_content = section.get('defaultContent', '')
                    # Only include greeting if enabled AND new conversation
                    if section_name == 'greeting' and not is_new_conversation:
                        continue
                    if section_name == 'next steps' and not include_next_steps:
                        continue
                    if section_name == 'sign off' and not include_sign_off:
                        continue
                    if section_name == 'greeting':
                        section_text = section_content
                    elif section_name == 'main content':
                        ai_text_to_use = ai_response_text.strip() if ai_response_text else ''
                        # If AI answer is empty or matches opt-in prompt, use fallback
                        opt_in_prompt = (
                            workflow.actions.get('twilio', {}).get('optInPrompt') or
                            "Reply YES to receive SMS updates. Reply STOP to opt out."
                        )
                        def normalize(text):
                            return re.sub(r'[^a-z0-9]', '', (text or '').lower())
                        if not ai_text_to_use or normalize(ai_text_to_use) == normalize(opt_in_prompt):
                            logger.warning(f"AI response was empty or matched opt-in prompt, using fallback.")
                            ai_text_to_use = workflow.actions.get('twilio', {}).get('fallbackMessage') or workflow.actions.get('response', {}).get('fallbackMessage') or "Thank you for your message. We'll respond shortly."
                        section_text = ai_text_to_use or section_content
                    else:
                        section_text = section_content
                    if section_text:
                        if response_text:
                            response_text += "\n"
                        response_text += section_text
            response_text = response_text.strip()
        else:
            response_text = ai_response_text or (
                workflow.actions.get('twilio', {}).get('fallbackMessage') or
                workflow.actions.get('response', {}).get('fallbackMessage') or
                "Thank you for your message. We'll respond shortly."
            )
        if include_opt_in_prompt:
            opt_in_prompt = (
                workflow.actions.get('twilio', {}).get('optInPrompt') or
                "Reply YES to receive SMS updates. Reply STOP to opt out."
            )
            # Only append if not already present (case-insensitive, whitespace-insensitive)
            def normalize(text):
                return re.sub(r'[^a-z0-9]', '', (text or '').lower())
            if normalize(opt_in_prompt) not in normalize(response_text):
                if response_text:
                    response_text = f"{response_text}\n\n{opt_in_prompt}"
                else:
                    response_text = opt_in_prompt
        # Final deduplication: ensure opt-in prompt appears only once
        norm_prompt = normalize(opt_in_prompt)
        lines = []
        seen_prompt = False
        for ln in response_text.split("\n"):
            if normalize(ln) == norm_prompt:
                if seen_prompt:
                    continue
                seen_prompt = True
            lines.append(ln)
        response_text = "\n".join(lines).strip()
        logger.info(f"AI response used: {ai_response_text}")
        logger.info(f"Final SMS body: {response_text}")
        resp.message(response_text)
        # Store outgoing message
        session = SessionLocal()
        try:
            outgoing_message = Message(
                workflow_id=workflow.id,
                direction=MessageDirection.OUTBOUND,
                channel=MessageChannel.SMS,
                content=response_text,
                phone_number=from_number,
                conversation_id=current_conversation_id,
                response_to_message_id=incoming_message_id if incoming_message_id else None,
                status=MessageStatus.SENT
            )
            session.add(outgoing_message)
            session.commit()
        except Exception as db_error:
            logger.error(f"Error storing outgoing message: {str(db_error)}")
            session.rollback()
        finally:
            session.close()
        return Response(content=str(resp), media_type="application/xml")
    except Exception as e:
        logger.error(f"ERROR PROCESSING BUSINESS-SPECIFIC WEBHOOK: {str(e)}")
        resp.message("Thank you for your message. Our team will respond shortly.")
        return Response(content=str(resp), media_type="application/xml")

@router.api_route("/webhook-test", methods=["GET", "POST"])
def webhook_test(request: Request, db: Session = Depends(get_db)):
    # Implement webhook test logic
    return {"detail": "Webhook test endpoint hit (mock)"}
