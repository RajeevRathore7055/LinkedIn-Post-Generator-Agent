"""
Utility functions: LLM client wrapper, retries, error handling, and helpers.
"""

import logging
import os
import time
from typing import Optional

logger = logging.getLogger("linkedin_agent")
logging.basicConfig(level=logging.INFO)


class LLMError(Exception):
    """Raised when the LLM call fails after retries."""


class MissingAPIKeyError(Exception):
    """Raised when no valid API key is configured."""


def get_groq_client():
    """
    Lazily initialize and return a configured Groq client instance.

    Raises:
        MissingAPIKeyError: if GROQ_API_KEY is not set.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise MissingAPIKeyError(
            "GROQ_API_KEY is not set. Please configure it in your .env file."
        )

    from groq import Groq

    return Groq(api_key=api_key)


def call_llm(prompt: str, max_retries: int = 3, timeout: int = 30) -> str:
    """
    Call the configured LLM (Groq) with retry and timeout handling.

    Args:
        prompt: The prompt text to send to the model.
        max_retries: Number of retry attempts on transient failure.
        timeout: Request timeout in seconds passed to the Groq client.

    Returns:
        The generated text response, stripped of whitespace.

    Raises:
        MissingAPIKeyError: if the API key is missing.
        LLMError: if all retry attempts fail.
    """
    client = get_groq_client()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    last_exception: Optional[Exception] = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024,
                timeout=timeout,
            )
            text = response.choices[0].message.content if response.choices else None
            if not text:
                raise LLMError("Empty response received from the model.")
            return text.strip()
        except MissingAPIKeyError:
            raise
        except Exception as exc:  # noqa: BLE001 - broad catch is intentional for retries
            last_exception = exc
            logger.warning("LLM call attempt %s/%s failed: %s", attempt, max_retries, exc)
            if attempt < max_retries:
                time.sleep(min(2 ** attempt, 8))

    raise LLMError(f"LLM call failed after {max_retries} attempts: {last_exception}")


def parse_hashtags(raw_text: str) -> list[str]:
    """
    Parse a comma-separated hashtag string returned by the LLM into a clean list.

    Args:
        raw_text: Raw text returned by the model, expected comma-separated hashtags.

    Returns:
        A de-duplicated list of hashtags, each guaranteed to start with '#'.
    """
    if not raw_text:
        return []

    parts = [p.strip() for p in raw_text.replace("\n", ",").split(",")]
    hashtags = []
    seen = set()
    for part in parts:
        if not part:
            continue
        tag = part if part.startswith("#") else f"#{part}"
        tag = tag.replace(" ", "")
        if tag.lower() not in seen and len(tag) > 1:
            seen.add(tag.lower())
            hashtags.append(tag)
    return hashtags

