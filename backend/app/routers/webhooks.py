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
from ..utils.date_extractor import extract_date_time
from ..utils.calendly_helper import verify_appointment_with_service, format_appointment_response

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
        # Updated to use status='ACTIVE' instead of is_active=True
        workflow = db.query(Workflow).filter(
            Workflow.business_id == business_id, 
            Workflow.status == 'ACTIVE'
        ).first()
        
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
        # Prepare body for pattern matching - lowercase for case insensitivity
        body_text = body.strip() if body else ''
        body_upper = body_text.upper()
        body_lower = body_text.lower()
        
        # Very flexible YES detection with multiple patterns
        # 1. Exactly "yes" (any case)
        # 2. Starts with "yes" followed by space, comma, period
        # 3. Contains "yes" as a standalone word
        if (body_upper == 'YES' or 
            re.match(r'^yes[\s,.;:]', body_lower, re.IGNORECASE) or
            re.search(r'\byes\b', body_lower, re.IGNORECASE)):
            if consent_record.status != 'CONFIRMED':
                consent_record.status = 'CONFIRMED'
                db.commit()
                logger.info(f"User {from_number} opted in with message: '{body}'")
            resp.message("Thanks! You've opted in to receive SMS updates. Reply STOP to opt out anytime.")
            return Response(content=str(resp), media_type="application/xml")
            
        # Keep STOP handling strict to avoid accidental opt-outs
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
            
            # Check if this is an appointment-related query
            appointment_keywords = ['appointment', 'booking', 'schedule', 'consultation', 'availability', 'times']
            is_appointment_query = any(keyword in body.lower() for keyword in appointment_keywords)
            
            # Check if this is a booking request (user wants to book a specific time)
            booking_keywords = ['book', "let's book", 'schedule me', 'make an appointment', 'reserve']
            is_booking_request = any(keyword in body.lower() for keyword in booking_keywords)
            
            logger.info(f"[CALENDLY DEBUG] Checking message: '{body}' - Query: {is_appointment_query}, Booking: {is_booking_request}")
            
            # Initialize appointment context as None
            appointment_context = None
            
            # Handle booking request first
            if is_booking_request:
                try:
                    # Import the booking function
                    from ..utils.calendly_helper import create_appointment_with_service
                    
                    # Extract date/time from message
                    date_info = extract_date_time(body)
                    logger.info(f"[CALENDLY DEBUG] Extracted date info for booking: {date_info}")
                    
                    if date_info and date_info.get("datetime"):
                        # We have a date, try to create the appointment
                        booking_date = date_info.get("datetime")
                        
                        # Attempt to find contact info (use placeholder if not found)
                        # In a real implementation, you'd get this from your database or prompt the user
                        customer_name = "SMS Customer"  # Placeholder
                        customer_email = "customer@example.com"  # Placeholder
                        customer_phone = from_number
                        
                        # Create the appointment
                        booking_result = await create_appointment_with_service(
                            workflow.id,
                            booking_date,
                            customer_name,
                            customer_email,
                            customer_phone
                        )
                        
                        logger.info(f"[CALENDLY DEBUG] Booking result: {booking_result}")
                        
                        # Provide booking result context to AI
                        appointment_context = {
                            "booking_result": booking_result,
                            "booking_date": booking_date.isoformat(),
                            "is_booking_request": True,
                            "success": booking_result.get("success", False)
                        }
                    else:
                        # No date found, provide context to AI
                        appointment_context = {
                            "is_booking_request": True,
                            "success": False,
                            "error": "No date found",
                            "message": "Could not determine what date/time you want to book"
                        }
                except Exception as e:
                    logger.error(f"[CALENDLY DEBUG] Error creating appointment: {str(e)}")
                    import traceback
                    logger.error(f"[CALENDLY DEBUG] {traceback.format_exc()}")
                    
                    # Provide error context to AI
                    appointment_context = {
                        "is_booking_request": True,
                        "success": False,
                        "error": "Booking error",
                        "message": str(e)
                    }
            
            # Handle appointment query (checking availability)
            elif is_appointment_query:
                try:                    
                    # Log the workflow actions for debugging
                    logger.info(f"[CALENDLY DEBUG] Workflow actions keys: {list(workflow.actions.keys() if workflow.actions else [])}")
                    logger.info(f"[CALENDLY DEBUG] Calendly config: {workflow.actions.get('calendly', {})}")
                    
                    # Extract date/time from message
                    date_info = extract_date_time(body)
                    logger.info(f"[CALENDLY DEBUG] Extracted date info: {date_info}")
                    
                    # Use current date as fallback
                    search_date = date_info.get("datetime") if date_info and date_info.get("datetime") else datetime.now()
                    
                    # Always try to call the Calendly verification service directly
                    logger.info(f"[CALENDLY DEBUG] Calling verify_appointment_with_service with date: {search_date}")
                    verification_result = await verify_appointment_with_service(
                        workflow.id, 
                        search_date
                    )
                    
                    logger.info(f"[CALENDLY DEBUG] Verification result: {verification_result}")
                    
                    # If successful, use the result
                    if verification_result.get("success"):
                        # Format a human-readable response
                        appointment_response = format_appointment_response(verification_result)
                        logger.info(f"[CALENDLY DEBUG] Formatted response: {appointment_response}")
                        
                        # Add context to AI service
                        appointment_context = {
                            "verification_result": verification_result,
                            "formatted_response": appointment_response,
                            "is_general_availability": not (date_info and date_info.get("datetime")),
                            "search_date": search_date.isoformat()
                        }
                        
                        if date_info and date_info.get("datetime"):
                            appointment_context["extracted_date"] = date_info["datetime"].isoformat()
                            appointment_context["confidence"] = date_info["confidence"]
                        
                        logger.info(f"[CALENDLY DEBUG] Appointment verification context: {appointment_context}")
                    else:
                        # Log failure but continue
                        logger.error(f"[CALENDLY DEBUG] Verification failed: {verification_result.get('error')}")
                        logger.error(f"[CALENDLY DEBUG] Error message: {verification_result.get('message')}")
                        
                        # Still provide some context to AI
                        appointment_context = {
                            "error": verification_result.get("error", "Unknown error"),
                            "message": verification_result.get("message", "Failed to verify appointment"),
                            "is_error": True
                        }
                except Exception as e:
                    logger.error(f"[CALENDLY DEBUG] Error in appointment verification: {str(e)}")
                    # Log the full stack trace for debugging
                    import traceback
                    logger.error(f"[CALENDLY DEBUG] {traceback.format_exc()}")
                    
                    # Provide error context to AI
                    appointment_context = {
                        "error": "Exception during verification",
                        "message": str(e),
                        "is_error": True
                    }
            
            # Call AI service
            workflow_response = ai_service.analyze_requirements(
                body,
                workflow.actions,
                conversation_history=conversation_history,
                is_new_conversation=is_new_conversation,
                appointment_context=appointment_context
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
