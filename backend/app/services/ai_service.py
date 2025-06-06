import os
from typing import Dict, List, Optional, Union
import openai
from pydantic import BaseModel
import json  # Ensure json is imported at the module level
import logging
import re
from utils.api_keys import get_openai_api_key

# Constants for JSON templates to prevent f-string formatting issues
JSON_RESPONSE_TEMPLATE = '''
{
    "message": "Your direct response to the user without any greetings or sign-offs",
    "twilio": {
        "include_greeting": true,
        "include_sign_off": false
    }
}
'''


class WorkflowConfig(BaseModel):
    twilio: Dict[str, str] = {}
    sendgrid: Dict[str, str] = {}
    zendesk: Dict[str, str] = {}
    instructions: List[str] = []

class AIService:
    def __init__(self):
        self.system_prompt = """You are an AI assistant that helps create customer service automation workflows.
        Given a business description and requirements, generate a workflow configuration using Twilio, SendGrid, and Zendesk.
        Focus on practical, efficient solutions that improve customer experience.
        IMPORTANT: When asked to answer a user question for SMS, ONLY provide the direct answer to the user's question. DO NOT include any template placeholders (such as {content}) or opt-in prompts (such as 'Reply YES to receive SMS updates'). DO NOT include greetings or sign-offs unless specifically requested. DO NOT repeat or reference any template language. Your response will be inserted directly into the message body by the system."""

    def analyze_requirements(self, description: str, actions=None, conversation_history=None, is_new_conversation=False, appointment_context=None) -> Union[WorkflowConfig, Dict]:
        """Analyze natural language requirements and generate workflow configuration or response."""
        try:
            # Enhanced logging for troubleshooting
            logger = logging.getLogger(__name__)
            logger.info(f"AI Service analyzing: {description[:50]}...")
            logger.info(f"Actions provided: {bool(actions)}")
            logger.info(f"Conversation history provided: {bool(conversation_history)}")
            logger.info(f"Is new conversation: {is_new_conversation}")
            
            # Configure the OpenAI API key
            api_key = get_openai_api_key(actions)
            if not api_key:
                raise ValueError("No OpenAI API key found in environment variables")
                
            # Handle different versions of OpenAI client
            client = None
            try:
                # Try new format first
                logger.info("Setting up OpenAI client with workflow API key")
                client = openai.OpenAI(api_key=api_key)
            except (AttributeError, TypeError) as e:
                # Fall back to older client format
                logger.info("Trying older OpenAI API format")
                openai.api_key = api_key
                client = openai

            # Handle SMS response generation with actions provided from workflow
            if actions:
                # Re-evaluate API key with helper in case actions override
                api_key = get_openai_api_key(actions, explicit_key=api_key)
                logger.info(f"Using OpenAI key from workflow config: {'Available' if api_key else 'Missing'}")
                
                if not api_key:
                    logger.error("No OpenAI API key found in workflow config or environment")
                    return {"message": "I apologize, but I'm unable to process your request at this time."}
                
                # Build system prompt from brand voice settings
                brand_tone = actions.get('brandTone', {})
                voice_type = brand_tone.get('voiceType', 'professional')
                greetings = brand_tone.get('greetings', [])
                words_to_avoid = brand_tone.get('wordsToAvoid', [])
                
                # Build context from various config settings
                context_data = actions.get('context', {})
                qa_pairs = actions.get('aiTraining', {}).get('qaPairs', [])
                
                # Get message structure info for context
                message_structure = actions.get('response', {}).get('messageStructure', [])
                has_structure = bool(message_structure and isinstance(message_structure, list))
                
                # Build structure info for the prompt
                structure_info = ""
                if has_structure:
                    section_names = [section.get('name', '').lower() for section in message_structure 
                                   if section.get('enabled', True)]
                    structure_info = "Message sections available: " + ", ".join(section_names)
                
                # Prepare any JSON data outside the f-string to avoid formatting issues
                qa_pairs_json = json.dumps(qa_pairs) if qa_pairs else "No specific FAQ data provided."
                context_data_json = json.dumps(context_data) if context_data else "No specific context provided."
                
                # Add appointment information if available
                appointment_info = ""
                if appointment_context:
                    logger.info(f"Including appointment context in prompt: {appointment_context}")
                    appointment_info = f"""
                    IMPORTANT - APPOINTMENT INFORMATION:
                    The user is asking about an appointment. Here is the verified information:
                    {appointment_context.get('formatted_response', 'No appointment information available.')}
                    
                    This information comes directly from the scheduling system. Use this verified information
                    in your response rather than making assumptions about appointments.
                    """
                
                # Create a comprehensive system prompt - use normal string first and then format it
                # to avoid nested formatting issues
                system_prompt_template = """
                You are a human customer service agent providing {voice_type} responses via SMS text messages.
                
                Communication Style Guidelines:
                - Be natural, conversational, and authentically human-like in your tone
                - Remember you are texting the customer directly on their phone
                - Use a {voice_type} tone that feels like a real person, not an AI
                - IMPORTANT: DO NOT include any greeting (like 'Hello' or 'Hi') in your response; greetings are handled separately
                - IMPORTANT: DO NOT start with 'How can I assist you' or similar phrases; just answer the query directly
                - IMPORTANT: DO NOT include any template placeholders or bracketed text like [method of communication]
                - IMPORTANT: DO NOT use phrases that sound robotic or templated
                - IMPORTANT: ALWAYS refer to SMS or texting as the communication method, never use placeholders
                - Words to avoid: {words_to_avoid_str}
                - Keep responses under 160 characters when possible
                - Be helpful, concise, and authentic
                
                Conversation Context:
                - This is a {conversation_type} via text message
                - {structure_info}
                - IMPORTANT: Your response will be used as the "Main Content" section of a structured message
                - Other sections like Greeting, Next Steps, and Sign Off will be handled separately
                - You should provide a direct, human-like answer as if you're texting the customer
                
                {appointment_info}
                
                Response Format:
                YOU MUST return a valid JSON object with this structure:
                ```json
                {JSON_RESPONSE_TEMPLATE}
                ```

                Note: Set include_greeting to true if a greeting should be included.
                Set include_sign_off to false if sign-off should be excluded.
                
                FAQ Knowledge:
                {qa_pairs_json}
                
                Context Information:
                {context_data_json}
                
                Along with your response, provide metadata about which sections should be included:
                - Indicate if the user appears to be asking for instructions or next steps
                - Indicate if the message seems like it's ending the conversation
                
                Respond directly to the user's message.
                """
                
                # Prepare all the string variables separately to avoid nested formatting issues
                words_to_avoid_str = ', '.join(words_to_avoid) if words_to_avoid else 'N/A'
                conversation_type = "new conversation" if is_new_conversation else "continuing conversation"
                
                # Apply formatting to the template
                system_prompt = system_prompt_template.format(
                    voice_type=voice_type,
                    words_to_avoid_str=words_to_avoid_str,
                    conversation_type=conversation_type,
                    structure_info=structure_info,
                    appointment_info=appointment_info,
                    JSON_RESPONSE_TEMPLATE=JSON_RESPONSE_TEMPLATE,
                    qa_pairs_json=qa_pairs_json,
                    context_data_json=context_data_json
                )
                
                logger.info(f"Using system prompt: {system_prompt[:100]}...")
                
                # Call OpenAI API with explicit client
                logger.info("Calling OpenAI API...")
                
                # Build message list with conversation history
                messages = [{"role": "system", "content": system_prompt}]
                
                # Add conversation history if available
                if conversation_history and len(conversation_history) > 0:
                    messages.extend(conversation_history)
                
                # Add the current user message
                messages.append({"role": "user", "content": description})
                
                try:
                    # Detect OpenAI version and use appropriate API calls
                    # First try newer client format with more robust error handling
                    try:
                        logger.info("Using new OpenAI client format")
                        # First check if we have a client instance already
                        if client:
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=messages,
                                temperature=0.7,
                                max_tokens=500,
                                response_format={"type": "json_object"}
                            )
                            message_content = response.choices[0].message.content.strip()
                        else:
                            # Try to create a client and use it (for newer versions)
                            try:
                                from openai import OpenAI
                                local_client = OpenAI(api_key=api_key)
                                response = local_client.chat.completions.create(
                                    model="gpt-3.5-turbo",
                                    messages=messages,
                                    temperature=0.7,
                                    max_tokens=500,
                                    response_format={"type": "json_object"}
                                )
                                message_content = response.choices[0].message.content.strip()
                            except Exception as new_client_error:
                                logger.error(f"Error with new client format: {str(new_client_error)}")
                                raise
                    except Exception as e:
                        # Fall back to legacy format
                        logger.info(f"New client format failed, trying legacy format: {str(e)}")
                        # Legacy OpenAI API call (prior to 1.0.0)
                        try:
                            # Fallback to even older format without response_format
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=messages,
                                temperature=0.7,
                                max_tokens=500
                            )
                            
                            message_content = response.choices[0].message.content.strip()
                        except Exception as legacy_error:
                            logger.error(f"Error with legacy client format: {str(legacy_error)}")
                            raise
                    
                    # Log the raw response for debugging
                    logger.info(f"Raw OpenAI response: {message_content[:100]}...")
                    
                    try:
                        # Parse JSON response
                        response_obj = json.loads(message_content)
                        
                        # Extract the actual response text
                        response_text = response_obj.get('message', '')
                        logger.info(f"Extracted response text: {response_text[:50]}...")
                        
                        # First clean the response text of any common greeting patterns
                        response_text = self.clean_common_greetings(response_text)
                        
                        # Get structure flags
                        twilio_data = response_obj.get('twilio', {})
                        include_greeting = twilio_data.get('include_greeting', is_new_conversation)
                        include_sign_off = twilio_data.get('include_sign_off', True)
                        
                        return {
                            'message': response_text,
                            'twilio': {
                                'include_greeting': include_greeting,
                                'include_sign_off': include_sign_off
                            }
                        }
                    except Exception as json_err:
                        logger.error(f"Failed to parse JSON response: {str(json_err)}")
                        # More aggressive cleanup for JSON-like content
                        cleaned_response = self.extract_message_from_malformed_json(message_content)
                        logger.info(f"Using cleaned fallback response: {cleaned_response[:50]}...")
                        
                        return {
                            'message': cleaned_response,
                            'twilio': {
                                'include_greeting': is_new_conversation,
                                'include_sign_off': True
                            }
                        }
                except Exception as api_error:
                    logger.error(f"OpenAI API error: {str(api_error)}")
                    
                    # Check for specific error types and provide better fallback messages
                    error_str = str(api_error).lower()
                    if "exceeded your current quota" in error_str or "insufficient_quota" in error_str:
                        logger.error("OpenAI API quota exceeded error - using fallback message")
                        return {
                            "message": "Thank you for your message. Our AI assistant is currently unavailable. A team member will respond to you shortly.",
                            "twilio": {
                                "include_greeting": is_new_conversation,
                                "include_sign_off": True
                            }
                        }
                    elif "rate limit" in error_str:
                        logger.error("OpenAI API rate limit error - using fallback message")
                        return {
                            "message": "Thank you for your message. Our system is experiencing high demand. Please try again in a few minutes.",
                            "twilio": {
                                "include_greeting": is_new_conversation,
                                "include_sign_off": True
                            }
                        }
                    else:
                        # Generic fallback for other errors
                        logger.error(f"Unhandled OpenAI API error: {error_str}")
                        return {
                            "message": "Thank you for your message. We've received it and will respond shortly.",
                            "twilio": {
                                "include_greeting": is_new_conversation,
                                "include_sign_off": True
                            }
                        }
                except Exception as general_error:
                    logger.error(f"General error calling OpenAI API: {str(general_error)}")
                    return {
                        "message": "Thank you for your message. We've received it and will respond shortly.",
                        "twilio": {
                            "include_greeting": is_new_conversation,
                            "include_sign_off": True
                        }
                    }
                
            else:
                # Original workflow config generation logic
                # Use system OpenAI key if available
                logger.info("Using system OpenAI API key")
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    logger.error("No OpenAI API key found in environment")
                    return WorkflowConfig()
                    
                client = openai.OpenAI(api_key=api_key)
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": description}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )

                # Parse the AI response into structured workflow config
                config = self._parse_ai_response(response.choices[0].message.content)
                
                # Generate setup instructions
                instructions = self._generate_setup_instructions(config)
                config.instructions = instructions
                
                return config
        except Exception as e:
            # Log the error but return a fallback response to prevent system failures
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to analyze requirements: {str(e)}")
            
            # Return a fallback response that won't break the SMS flow
            return {
                "message": "I apologize, but I'm having trouble understanding your request. Could you please rephrase it?",
                "twilio": {
                    "include_greeting": False,
                    "include_sign_off": True
                }
            }

    def _parse_ai_response(self, response: str) -> WorkflowConfig:
        """Parse AI response into structured workflow configuration."""
        try:
            # Initialize default workflow
            workflow = WorkflowConfig()

            # Add Twilio configuration if messaging/voice/chat is mentioned
            if any(keyword in response.lower() for keyword in ['sms', 'voice', 'chat', 'whatsapp']):
                workflow.twilio = {
                    'type': 'flex' if 'chat' in response.lower() else 'sms',
                    'aiEnabled': 'true' if 'ai' in response.lower() else 'false'
                }

            # Add SendGrid configuration if email is mentioned
            if 'email' in response.lower():
                workflow.sendgrid = {
                    'type': 'template',
                    'category': 'notification' if 'notification' in response.lower() else 'marketing'
                }

            # Add Zendesk configuration if support/tickets are mentioned
            if any(keyword in response.lower() for keyword in ['support', 'ticket', 'help']):
                workflow.zendesk = {
                    'type': 'ticket',
                    'priority': 'normal',
                    'category': 'support'
                }

            return workflow
        except Exception as e:
            raise Exception(f"Failed to parse AI response: {str(e)}")

    def _generate_setup_instructions(self, workflow: WorkflowConfig) -> List[str]:
        """Generate setup instructions based on workflow configuration."""
        instructions = []

        if workflow.twilio:
            instructions.extend([
                "Set Twilio webhook URL to /twilio/webhook",
                f"Configure Twilio {workflow.twilio['type']} settings in the dashboard"
            ])

        if workflow.sendgrid:
            instructions.extend([
                "Set SendGrid webhook URL to /sendgrid/webhook",
                "Verify sender domain in SendGrid dashboard"
            ])

        if workflow.zendesk:
            instructions.extend([
                "Configure Zendesk API credentials",
                "Set up ticket categories and routing rules"
            ])

        return instructions

    def generate_email_response(self, 
        customer_email: str, 
        brand_voice: Dict,
        template_id: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """Generate an AI response to a customer email."""
        try:
            # Build the system prompt with brand voice
            system_prompt = f"""You are an AI customer service agent. 
            Use this brand voice: {brand_voice.get('voiceType', 'professional')}
            Greetings to use: {', '.join(brand_voice.get('greetings', ['Hello']))}
            Words to avoid: {', '.join(brand_voice.get('wordsToAvoid', []))}
            
            Generate a helpful, on-brand response to the customer email."""

            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": "user" if msg["from"] == "customer" else "assistant",
                        "content": msg["content"]
                    })
            
            # Add the current customer email
            messages.append({"role": "user", "content": customer_email})

            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("No OpenAI API key found in environment variables")
                
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            reply = response.choices[0].message.content

            # If a template is specified, extract variables and format response
            if template_id:
                variables = self._extract_email_variables(reply, template_id)
                return {
                    "template_id": template_id,
                    "template_data": variables,
                    "type": "template"
                }
            else:
                return {
                    "content": reply,
                    "type": "custom"
                }

        except Exception as e:
            raise Exception(f"Failed to generate email response: {str(e)}")

    def _extract_email_variables(self, content: str, template_id: str) -> Dict:
        """Extract variables from AI response to fit into a template."""
        try:
            # Ask GPT to extract variables
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("No OpenAI API key found in environment variables")
                
            client = openai.OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract key information from this customer service response to fit into an email template."},
                    {"role": "user", "content": f"Extract variables from this response: {content}"}
                ],
                temperature=0.3,
                max_tokens=500
            )

            # Parse the response into a dictionary
            extracted = {}
            lines = response.choices[0].message.content.split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    extracted[key.strip()] = value.strip()

            return extracted

        except Exception as e:
            raise Exception(f"Failed to extract email variables: {str(e)}")

    def extract_message_from_malformed_json(self, text):
        """
        Extract the actual message content from malformed JSON responses.
        This handles cases where OpenAI returns JSON-like content that isn't valid JSON.
        """
        import re
        logger = logging.getLogger(__name__)
        
        # First attempt: Try to extract "message" field using regex
        message_match = re.search(r'"message"\s*:\s*"([^"]+)"', text)
        if message_match:
            logger.info("Extracted message content using regex pattern match")
            extracted_message = message_match.group(1)
            return self.clean_common_greetings(extracted_message)
        
        # Second attempt: Look for JSON-like structure and strip it
        if '{' in text and '}' in text:
            # Try to extract text between quotes that's not part of a JSON key
            logger.info("Attempting to clean JSON-like structure from text")
            # Remove anything that looks like JSON structure
            cleaned = re.sub(r'[{\[\]}":]', ' ', text)
            # Remove common JSON field names
            cleaned = re.sub(r'\b(message|twilio|include_greeting|include_sign_off)\b', '', cleaned)
            # Clean up extra whitespace
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned:
                logger.info(f"Extracted content by removing JSON structure: {cleaned[:50]}...")
                return self.clean_common_greetings(cleaned)
        
        # If all else fails, just use the original text with greeting cleaning
        logger.info("Falling back to basic greeting cleaning")
        return self.clean_common_greetings(text)

    def clean_common_greetings(self, text):
        import re
        # List of common greeting patterns to remove
        greeting_patterns = [
            r'^Hello!?\s+',
            r'^Hi!?\s+',
            r'^Hey!?\s+',
            r'^Greetings!?\s+',
            r'^Good\s+(morning|afternoon|evening|day)!?\s+',
            r'(Hello|Hi|Hey)!?,?\s+how\s+(can\s+I\s+|may\s+I\s+|I\s+can\s+)?(help|assist)\s+you\s+(today|now|with\s+that)?\??',
            r'How\s+can\s+I\s+(help|assist)\s+you\s+(today|now|with\s+that)?\??',
            r"I('m| am)\s+here\s+to\s+help.*?\.",
            r"I('m| am)\s+here\s+to\s+assist.*?\.",
            r"I\s+can\s+help\s+you\s+with.*?\.",
            # Common closing templates
            r'Here\s+are\s+the\s+next\s+steps:?\s*(\{steps\})?.*',
            r'Best\s+regards,?.*$',
            r'Sincerely,?.*$',
            r'Thank\s+you.*,?.*$',
            r'Thanks,?.*$',
            r'Regards,?.*$',
            r'Kind(ly|est)?\s+regards,?.*$',
            r'Let\s+me\s+know\s+if\s+you\s+have\s+any\s+other\s+questions.*?$',
            r'.*?feel\s+free\s+to\s+ask.*?$'
        ]
        
        # Apply each pattern
        result = text
        for pattern in greeting_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        result = result.strip()
        # If cleaning removes everything, fall back to original text
        if not result and text.strip():
            return text.strip()
        return result
