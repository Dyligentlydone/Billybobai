import os
from typing import Dict, List, Optional, Union
import openai
from pydantic import BaseModel
import json  # Ensure json is imported at the module level
import logging
import re

class WorkflowConfig(BaseModel):
    twilio: Dict[str, str] = {}
    sendgrid: Dict[str, str] = {}
    zendesk: Dict[str, str] = {}
    instructions: List[str] = []

class AIService:
    def __init__(self):
        self.system_prompt = """You are an AI assistant that helps create customer service automation workflows.
        Given a business description and requirements, generate a workflow configuration using Twilio, SendGrid, and Zendesk.
        Focus on practical, efficient solutions that improve customer experience."""

    def analyze_requirements(self, description: str, actions=None, conversation_history=None, is_new_conversation=False) -> Union[WorkflowConfig, Dict]:
        """Analyze natural language requirements and generate workflow configuration or response."""
        try:
            # Enhanced logging for troubleshooting
            logger = logging.getLogger(__name__)
            logger.info(f"AI Service analyzing: {description[:50]}...")
            logger.info(f"Actions provided: {bool(actions)}")
            logger.info(f"Conversation history provided: {bool(conversation_history)}")
            logger.info(f"Is new conversation: {is_new_conversation}")
            
            # Handle SMS response generation with actions provided from workflow
            if actions:
                # Extract OpenAI API key from actions
                api_key = actions.get('aiTraining', {}).get('openAIKey')
                logger.info(f"Using OpenAI key from workflow config: {'Available' if api_key else 'Missing'}")
                
                if not api_key:
                    # Try to find API key in other possible locations in the config
                    api_key = (
                        actions.get('openAIKey') or 
                        actions.get('ai', {}).get('apiKey') or
                        os.getenv('OPENAI_API_KEY')
                    )
                    logger.info(f"Fallback OpenAI key found: {'Yes' if api_key else 'No'}")
                
                if not api_key:
                    logger.error("No OpenAI API key found in workflow config or environment")
                    return {"message": "I apologize, but I'm unable to process your request at this time."}
                
                # Set up OpenAI with the workflow's API key
                logger.info("Setting up OpenAI client with workflow API key")
                try:
                    client = openai.OpenAI(api_key=api_key)
                    logger.info("OpenAI client created successfully with new API format")
                except Exception as openai_error:
                    # Fallback for older OpenAI library versions
                    logger.warning(f"Error creating OpenAI client with new format: {str(openai_error)}")
                    logger.info("Trying older OpenAI API format")
                    # Use the old format API for older OpenAI versions
                    # No need to create a client, just set the API key
                    openai.api_key = api_key
                    client = None  # We'll handle this below
                
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
                
                # Create a comprehensive system prompt
                system_prompt = f"""
                You are an AI assistant providing {voice_type} responses via SMS.
                
                Voice Guidelines:
                - Use a {voice_type} tone
                - IMPORTANT: DO NOT include any greeting (like 'Hello' or 'Hi') in your response; greetings are handled separately
                - IMPORTANT: DO NOT start with 'How can I assist you' or similar phrases; just answer the query directly
                - IMPORTANT: DO NOT include any template placeholders like "{{steps}}" or "{{name}}" in your response
                - IMPORTANT: DO NOT end with phrases like "Here are the next steps:" or "Best regards"
                - Words to avoid: {', '.join(words_to_avoid) if words_to_avoid else 'N/A'}
                - Keep responses under 160 characters when possible
                - Be helpful, concise, and accurate
                
                Conversation Context:
                - This is a {("new conversation" if is_new_conversation else "continuing conversation")}
                - {structure_info}
                - IMPORTANT: Your response will be used as the "Main Content" section of a structured message
                - Other sections like Greeting, Next Steps, and Sign Off will be handled separately
                - You should ONLY provide the direct answer to the user's question
                
                FAQ Knowledge:
                {json.dumps(qa_pairs) if qa_pairs else "No specific FAQ data provided."}
                
                Context Information:
                {json.dumps(context_data) if context_data else "No specific context provided."}
                
                Along with your response, provide metadata about which sections should be included:
                - Indicate if the user appears to be asking for instructions or next steps
                - Indicate if the message seems like it's ending the conversation
                
                Respond directly to the user's message.
                """
                
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
                    # Check which client format to use
                    if client:
                        # New OpenAI client format
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=500,
                            response_format={"type": "json_object"}
                        )
                        
                        # Parse response from new client format
                        message_content = response.choices[0].message.content.strip()
                    else:
                        # Old OpenAI client format
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=500
                        )
                        
                        # Parse response from old client format
                        message_content = response.choices[0].message.content.strip()
                    
                    # Log the raw response for debugging
                    logger.info(f"Raw OpenAI response: {message_content[:100]}...")
                    
                    try:
                        # Parse JSON response
                        result = json.loads(message_content)
                        
                        # Add twilio flag if missing
                        if "twilio" not in result:
                            result["twilio"] = True
                            
                        return result
                    except json.JSONDecodeError as json_error:
                        logger.error(f"Failed to parse JSON response: {str(json_error)}")
                        # Return a proper structured response even if JSON parsing fails
                        return {
                            "message": message_content,  # Use the raw message as fallback
                            "twilio": True
                        }
                except Exception as api_error:
                    logger.error(f"OpenAI API error: {str(api_error)}")
                    
                    # Check for specific error types and provide better fallback messages
                    error_str = str(api_error).lower()
                    if "exceeded your current quota" in error_str or "insufficient_quota" in error_str:
                        logger.error("OpenAI API quota exceeded error - using fallback message")
                        return {
                            "message": "Thank you for your message. Our AI assistant is currently unavailable. A team member will respond to you shortly.",
                            "twilio": True
                        }
                    elif "rate limit" in error_str:
                        logger.error("OpenAI API rate limit error - using fallback message")
                        return {
                            "message": "Thank you for your message. Our system is experiencing high demand. Please try again in a few minutes.",
                            "twilio": True
                        }
                    else:
                        # Generic fallback for other errors
                        logger.error(f"Unhandled OpenAI API error: {error_str}")
                        return {
                            "message": "Thank you for your message. We've received it and will respond shortly.",
                            "twilio": True
                        }
                except Exception as general_error:
                    logger.error(f"General error calling OpenAI API: {str(general_error)}")
                    return {
                        "message": "Thank you for your message. We've received it and will respond shortly.",
                        "twilio": True
                    }
                
                # Clean any common greetings from the AI response that might have been included despite instructions
                def clean_common_greetings(text):
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
                        # Common closing templates
                        r'Here\s+are\s+the\s+next\s+steps:?\s*(\{steps\})?.*',
                        r'Best\s+regards,?.*$',
                        r'Sincerely,?.*$',
                        r'Thank\s+you.*,?.*$',
                        r'Thanks,?.*$',
                        r'Regards,?.*$',
                        r'Kind(ly|est)?\s+regards,?.*$',
                    ]
                    
                    # Apply each pattern
                    result = text
                    for pattern in greeting_patterns:
                        result = re.sub(pattern, '', result, flags=re.IGNORECASE)
                    
                    return result.strip()
                
                # Try to parse the AI response as JSON to extract metadata
                try:
                    response_obj = json.loads(message_content)
                    
                    # Extract the actual response text
                    if isinstance(response_obj, dict):
                        # Get the response text from the JSON
                        ai_message = response_obj.get('response', response_obj.get('message', ''))
                        
                        # Extract metadata about which sections to include
                        include_next_steps = response_obj.get('include_next_steps', 
                                                             response_obj.get('needs_next_steps', False))
                        include_sign_off = response_obj.get('include_sign_off', 
                                                           response_obj.get('is_conversation_ending', False))
                        
                        # Clean any remaining greetings
                        ai_message = clean_common_greetings(ai_message)
                        
                        # Return structured response with metadata
                        return {
                            "message": ai_message,
                            "include_next_steps": include_next_steps,
                            "include_sign_off": include_sign_off,
                            "twilio": True
                        }
                except (json.JSONDecodeError, AttributeError, TypeError) as json_error:
                    logger.warning(f"Failed to parse AI response as JSON: {str(json_error)}")
                    # Fall back to treating the whole response as a message
                
                # Clean any greetings from the message content
                message_content = clean_common_greetings(message_content)
                
                # Return the AI generated message
                return {
                    "message": message_content,
                    "include_next_steps": False,  # Default values when parsing fails
                    "include_sign_off": False,
                    "twilio": True  # Indicate this is a Twilio response
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
                "twilio": True
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
