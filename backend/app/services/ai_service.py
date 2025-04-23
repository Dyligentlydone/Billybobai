import os
from typing import Dict, List, Optional, Union
import openai
from pydantic import BaseModel

class WorkflowConfig(BaseModel):
    twilio: Dict[str, str] = {}
    sendgrid: Dict[str, str] = {}
    zendesk: Dict[str, str] = {}
    instructions: List[str] = []

class AIService:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.system_prompt = """You are an AI assistant that helps create customer service automation workflows.
        Given a business description and requirements, generate a workflow configuration using Twilio, SendGrid, and Zendesk.
        Focus on practical, efficient solutions that improve customer experience."""

    async def analyze_requirements(self, description: str, actions=None) -> Union[WorkflowConfig, Dict]:
        """Analyze natural language requirements and generate workflow configuration or response."""
        try:
            # If actions is provided, we're in SMS response mode (not config generation)
            if actions:
                # Use the provided workflow actions to generate a response to the SMS
                # Extract prompt from the workflow configuration if available
                ai_settings = actions.get('aiTraining', {})
                prompt = actions.get('twilio', {}).get('prompt', '')
                
                if not prompt:
                    # Fallback to creating a generic prompt
                    brand_tone = actions.get('brandTone', {}).get('voiceType', 'professional')
                    prompt = f"You are a {brand_tone} AI assistant responding to customer SMS messages."
                
                # Set up context from the workflow actions
                system_prompt = f"{prompt}\n\nRespond to the customer message briefly and professionally."
                
                # Use OpenAI to generate a response
                response = openai.chat.completions.create(
                    model=ai_settings.get('openAIModel', 'gpt-4'),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": description}
                    ],
                    temperature=actions.get('temperature', 0.7),
                    max_tokens=300  # Keep SMS responses brief
                )
                
                # Return the AI generated message
                return {
                    "message": response.choices[0].message.content.strip(),
                    "twilio": True  # Indicate this is a Twilio response
                }
            
            # Original workflow config generation logic
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Generate a workflow configuration for: {description}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Parse the AI response into structured workflow config
            workflow = self._parse_ai_response(response.choices[0].message.content)
            workflow.instructions.extend(self._generate_setup_instructions(workflow))
            return workflow
        except Exception as e:
            # Log the error but return a fallback response to prevent system failures
            import logging
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

    async def generate_email_response(self, 
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

            response = await openai.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            reply = response.choices[0].message.content

            # If a template is specified, extract variables and format response
            if template_id:
                variables = await self._extract_email_variables(reply, template_id)
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

    async def _extract_email_variables(self, content: str, template_id: str) -> Dict:
        """Extract variables from AI response to fit into a template."""
        try:
            # Ask GPT to extract variables
            response = await openai.chat.completions.create(
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
