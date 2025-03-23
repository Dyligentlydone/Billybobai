from typing import Dict, Optional, Tuple, NamedTuple
from openai import AsyncOpenAI
import tiktoken
import logging
from datetime import datetime

class ResponseResult(NamedTuple):
    text: str
    tokens_used: int
    model_used: str
    cost: float
    confidence: float

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.encoding = tiktoken.encoding_for_model("gpt-4")
        
        # Cost per 1K tokens (as of 2025)
        self.cost_rates = {
            'gpt-4': {'input': 0.01, 'output': 0.03},
            'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015}
        }

    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost based on token usage"""
        rates = self.cost_rates.get(model, self.cost_rates['gpt-3.5-turbo'])
        return (input_tokens * rates['input'] + output_tokens * rates['output']) / 1000

    async def generate_response(
        self,
        message: str,
        context: Dict,
        tone: str = 'professional',
        model: str = 'gpt-4',
        max_tokens: int = 300,
        temperature: float = 0.7
    ) -> ResponseResult:
        """Generate AI response for SMS message"""
        try:
            # Construct system prompt
            system_prompt = (
                f"You are an AI assistant communicating via SMS. "
                f"Maintain a {tone} tone. "
                f"Be concise as this is SMS. "
                f"Context: {context}"
            )

            # Count input tokens
            input_text = system_prompt + message
            input_tokens = len(self.encoding.encode(input_text))

            # Generate response
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0.6,  # Encourage varied responses
                frequency_penalty=0.5   # Reduce repetition
            )

            # Extract response text and token usage
            response_text = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens
            input_tokens = response.usage.prompt_tokens
            
            # Calculate cost and confidence
            total_cost = self._calculate_cost(input_tokens, output_tokens, model)
            confidence = response.choices[0].finish_reason == "stop"

            return ResponseResult(
                text=response_text,
                tokens_used=input_tokens + output_tokens,
                model_used=model,
                cost=total_cost,
                confidence=1.0 if confidence else 0.8
            )

        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise

# Module-level client instance
_client: Optional[OpenAIClient] = None

def initialize(api_key: str):
    """Initialize the OpenAI client"""
    global _client
    _client = OpenAIClient(api_key)

async def generate_response(*args, **kwargs) -> ResponseResult:
    """Module-level generate_response function"""
    if not _client:
        raise RuntimeError("OpenAI client not initialized. Call initialize() first.")
    return await _client.generate_response(*args, **kwargs)
