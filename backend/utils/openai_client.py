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
        
        # Create chat completion
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
        
        # Get response text
        text = response.choices[0].message.content.strip()
        
        # Calculate token usage and cost
        tokens_used = response.usage.total_tokens
        cost = calculate_cost(tokens_used, model)
        
        # Calculate confidence (based on model's own scoring)
        confidence = 1.0 - (response.choices[0].finish_reason == 'length')
        
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
