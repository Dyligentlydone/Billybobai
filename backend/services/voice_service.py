from typing import Dict, List, Optional
from twilio.twiml.voice_response import VoiceResponse, Gather
from services.ai_service import AIService

class VoiceService:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def generate_welcome_twiml(self, config: Dict) -> str:
        """Generate TwiML for the welcome message and main menu."""
        response = VoiceResponse()
        
        # Add initial greeting
        response.say(
            config['callFlow']['greeting'],
            voice=config['callFlow']['voicePreferences']['gender'],
            language=config['callFlow']['voicePreferences']['language']
        )
        
        # Add main menu
        gather = Gather(
            num_digits=1,
            action='/voice/handle-menu',
            method='POST',
            timeout=5
        )
        
        # Add menu prompt
        gather.say(
            config['callFlow']['mainMenu']['prompt'],
            voice=config['callFlow']['voicePreferences']['gender'],
            language=config['callFlow']['voicePreferences']['language']
        )
        
        # Add menu options
        for option in config['callFlow']['mainMenu']['options']:
            gather.say(
                f"Press {option['digit']} to {option['description']}",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
        
        response.append(gather)
        
        # Add fallback for no input
        response.redirect('/voice/welcome')
        
        return str(response)

    def handle_menu_selection(self, digit: str, config: Dict) -> str:
        """Handle menu selection and generate appropriate TwiML response."""
        response = VoiceResponse()
        
        # Find selected option
        selected_option = next(
            (opt for opt in config['callFlow']['mainMenu']['options'] 
             if opt['digit'] == digit),
            None
        )
        
        if not selected_option:
            # Invalid selection
            response.say(
                "Sorry, that's not a valid option. Let's try again.",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            response.redirect('/voice/welcome')
            return str(response)
        
        # Handle different actions
        if selected_option['action'] == 'message':
            # Use AI to generate response
            gather = Gather(
                input='speech',
                action='/voice/handle-input',
                method='POST',
                language=config['callFlow']['voicePreferences']['language'],
                speechTimeout='auto'
            )
            gather.say(
                "How can I help you today?",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            response.append(gather)
            
        elif selected_option['action'] == 'transfer':
            response.say(
                "Please hold while I transfer you to an agent.",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            # TODO: Implement actual transfer logic
            response.dial(config['business']['phone'])
            
        elif selected_option['action'] == 'voicemail':
            response.say(
                "Please leave a message after the tone.",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            response.record(
                action='/voice/handle-recording',
                maxLength=300,
                playBeep=True
            )
        
        return str(response)

    async def handle_voice_input(self, speech_result: str, config: Dict) -> str:
        """Handle voice input and generate AI response."""
        response = VoiceResponse()
        
        if not speech_result:
            response.say(
                "I didn't catch that. Could you please repeat?",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            response.redirect('/voice/welcome')
            return str(response)
        
        try:
            # Generate AI response
            ai_response = await self.ai_service.generate_response(
                speech_result,
                system_prompt=f"You are a voice assistant for {config['business']['name']}. " +
                            "Respond in a natural, conversational way. Keep responses concise and clear.",
                max_tokens=100  # Keep responses short for voice
            )
            
            # Convert response to speech
            response.say(
                ai_response,
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            
            # Ask if there's anything else
            gather = Gather(
                input='speech',
                action='/voice/handle-input',
                method='POST',
                language=config['callFlow']['voicePreferences']['language'],
                speechTimeout='auto'
            )
            gather.say(
                "Is there anything else I can help you with?",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            response.append(gather)
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            response.say(
                "I apologize, but I'm having trouble understanding. Let me transfer you to an agent.",
                voice=config['callFlow']['voicePreferences']['gender'],
                language=config['callFlow']['voicePreferences']['language']
            )
            response.dial(config['business']['phone'])
        
        return str(response)

    def handle_recording(self, recording_url: str, config: Dict) -> str:
        """Handle completed voicemail recording."""
        response = VoiceResponse()
        
        response.say(
            "Thank you for your message. We'll get back to you as soon as possible.",
            voice=config['callFlow']['voicePreferences']['gender'],
            language=config['callFlow']['voicePreferences']['language']
        )
        
        # TODO: Implement logic to store recording URL and notify business
        
        return str(response)
