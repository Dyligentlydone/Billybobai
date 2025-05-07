import os
import logging
from typing import Dict, Optional

def get_openai_api_key(config: Optional[Dict] = None, explicit_key: Optional[str] = None) -> Optional[str]:
    """Return the OpenAI API key.

    Priority order:
    1. ``explicit_key`` argument if provided.
    2. ``config['aiTraining']['openAIKey']`` if present.
    3. ``config['actions']['aiTraining']['openAIKey']`` if present.
    4. ``OPENAI_API_KEY`` environment variable.

    Returns ``None`` if the key is not found. Logs where the key was obtained (masked)."""
    # 1. Explicit key wins
    if explicit_key:
        return explicit_key.strip()

    key: Optional[str] = None

    # 2 & 3. Look inside workflow configuration dictionaries if provided
    if isinstance(config, dict):
        ai_training = config.get("aiTraining")
        if isinstance(ai_training, dict):
            key = ai_training.get("openAIKey")

        if not key and isinstance(config.get("actions"), dict):
            actions_ai = config["actions"].get("aiTraining")
            if isinstance(actions_ai, dict):
                key = actions_ai.get("openAIKey")

    # 4. Fallback to env var
    if not key:
        key = os.getenv("OPENAI_API_KEY")

    # Mask the key for logs (show first 4 chars only)
    if key:
        masked = key[:4] + "***"
        logging.info("Retrieved OpenAI API key (masked): %s", masked)
    else:
        logging.warning("OpenAI API key not found via helper")

    return key
