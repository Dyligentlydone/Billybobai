import os
from typing import Dict, List
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

    def analyze_requirements(self, description: str) -> WorkflowConfig:
        """Analyze natural language requirements and generate workflow configuration."""
        try:
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
            raise Exception(f"Failed to analyze requirements: {str(e)}")

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
