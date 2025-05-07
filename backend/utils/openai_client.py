import os
import logging
from typing import Dict, Optional, NamedTuple
from openai import AsyncOpenAI
import tiktoken
from utils.api_keys import get_openai_api_key

class AIResponse(NamedTuple):
    text: str
    tokens_used: int
    cost: float
    confidence: float
    model_used: str

# Global client instance
client = None

def initialize(api_key: Optional[str] = None):
    """Initialize the OpenAI client with API key"""
    global client
    # Prefer explicit key; otherwise fall back to helper which checks config/env vars
    key = api_key or get_openai_api_key()
    client = AsyncOpenAI(api_key=key)
    logging.info("Initialized OpenAI client (key masked)")

async def generate_response(
    message: str,
    context: Dict,
    tone: str = 'professional',
    model: str = 'gpt-3.5-turbo'
) -> AIResponse:
    """Generate an AI response for an SMS message"""
    try:
        if not client:
            initialize()
            
        # Format system prompt with context
        system_prompt = f"""You are an AI assistant for {context.get('business_name', 'our business')}.
Your role is to provide helpful, {tone} responses to customer inquiries via SMS.

Business Context:
- Name: {context.get('business_name', 'our business')}
- Common Questions: {', '.join(context.get('common_questions', []))}
- Products/Services: {context.get('product_info', {})}

Guidelines:
1. Keep responses concise and SMS-friendly (max 160 characters per segment)
2. Maintain a {tone} tone
3. Be direct and helpful
4. If you don't know something, say so
5. Include clear next steps when needed"""
        
        # Create chat completion with error handling for different client versions
        try:
            # Try the new client format first
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=150,  # Keep responses concise for SMS
                presence_penalty=0.6,  # Encourage varied responses
                frequency_penalty=0.2,  # Slightly reduce repetition
            )
        except AttributeError as e:
            # If 'chat' attribute error, try the legacy client format
            logging.warning(f"Using legacy OpenAI client format: {str(e)}")
            # For older versions of the OpenAI library
            from openai import Completion
            # Try with ChatCompletion first (pre-v1 API)
            try:
                response = await openai.ChatCompletion.acreate(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=150
                )
            except Exception as chat_error:
                logging.error(f"Legacy ChatCompletion failed: {str(chat_error)}")
                # Last resort fallback to even older Completion API
                response = await openai.Completion.acreate(
                    engine=model,
                    prompt=f"{system_prompt}\n\nUser: {message}\nAI:",
                    temperature=0.7,
                    max_tokens=150
                )
        
        # Parse response based on which client version was used
        try:
            # Try to get response from new client format first
            if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                text = response.choices[0].message.content.strip()
            # Fall back to older format if needed
            elif hasattr(response.choices[0], 'text'):
                text = response.choices[0].text.strip()
            else:
                # Last resort generic extraction
                text = str(response.choices[0]).strip()
                
            logging.info(f"Successfully extracted response text: {text[:50]}...")
        except Exception as parse_error:
            logging.error(f"Error parsing response: {str(parse_error)}")
            # Return a simple fallback response if we can't parse the response
            text = "Thank you for your message. We've received it and will respond shortly."
        
        # Calculate token usage and cost with error handling
        try:
            # Try to get token usage from response for newer client versions
            if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
                tokens_used = response.usage.total_tokens
            else:
                # Estimate token count if not available in response
                tokens_used = count_tokens(text) + count_tokens(system_prompt + message)
                logging.info(f"Estimated token usage: {tokens_used}")
            
            cost = calculate_cost(tokens_used, model)
            
            # Calculate confidence (safely handle different response formats)
            try:
                if hasattr(response.choices[0], 'finish_reason'):
                    confidence = 1.0 - (response.choices[0].finish_reason == 'length')
                else:
                    confidence = 0.8  # Default confidence if finish_reason not available
            except Exception:
                confidence = 0.8  # Default confidence value if any error occurs
        except Exception as usage_error:
            logging.error(f"Error calculating token usage: {str(usage_error)}")
            # Use fallback values
            tokens_used = 100  # Conservative estimate
            cost = calculate_cost(tokens_used, model)
            confidence = 0.7  # Lower confidence due to error
        
        return AIResponse(
            text=text,
            tokens_used=tokens_used,
            cost=cost,
            confidence=confidence,
            model_used=model
        )
        
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise

def calculate_cost(tokens: int, model: str) -> float:
    """Calculate cost in USD for token usage"""
    # Current OpenAI pricing (as of 2024)
    prices = {
        'gpt-4': 0.03,  # $0.03 per 1K tokens
        'gpt-4-32k': 0.06,  # $0.06 per 1K tokens
        'gpt-3.5-turbo': 0.0015,  # $0.0015 per 1K tokens
        'gpt-3.5-turbo-16k': 0.003  # $0.003 per 1K tokens
    }
    
    price_per_1k = prices.get(model, 0.0015)  # Default to gpt-3.5-turbo pricing
    return (tokens / 1000) * price_per_1k

def count_tokens(text: str, model: str = 'gpt-3.5-turbo') -> int:
    """Count the number of tokens in a text string"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logging.error(f"Error counting tokens: {str(e)}")
        return len(text.split()) * 1.3  # Rough estimate
