"""
API route definitions for the LinkedIn Post Generator Agent.
"""

import logging
import os

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.agent import run_agent_pipeline
from app.models import PostRequest, PostResponse
from app.utils import LLMError, MissingAPIKeyError

logger = logging.getLogger("linkedin_agent")

router = APIRouter()


@router.post("/generate", response_model=PostResponse)
async def generate_post_endpoint(request: PostRequest) -> PostResponse:
    """
    Generate a complete LinkedIn post using the multi-stage AI agent pipeline.

    Args:
        request: Validated PostRequest payload (topic, audience, tone, etc.)

    Returns:
        PostResponse containing the hook, final post body, and hashtags.

    Raises:
        HTTPException: 400 for invalid input, 401 for missing API key,
                        408 for timeouts, 429 for rate limits, 500 for
                        unexpected server errors.
    """
    try:
        result = run_agent_pipeline(request)
        return result

    except MissingAPIKeyError as exc:
        logger.error("Missing API key: %s", exc)
        raise HTTPException(
            status_code=401,
            detail="Server is missing a valid Groq API key. Please contact the administrator.",
        ) from exc

    except ValidationError as exc:
        logger.error("Validation error: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid input provided.") from exc

    except LLMError as exc:
        error_message = str(exc).lower()
        if "timeout" in error_message:
            logger.error("LLM timeout: %s", exc)
            raise HTTPException(
                status_code=408, detail="The AI service took too long to respond. Please try again."
            ) from exc
        if "rate limit" in error_message or "quota" in error_message or "429" in error_message:
            logger.error("Rate limit hit: %s", exc)
            raise HTTPException(
                status_code=429, detail="Rate limit reached. Please wait a moment and try again."
            ) from exc
        logger.error("LLM error: %s", exc)
        raise HTTPException(
            status_code=502, detail="The AI service failed to generate a response. Please try again."
        ) from exc

    except Exception as exc:  # noqa: BLE001 - top-level safety net
        logger.exception("Unexpected server error: %s", exc)
        raise HTTPException(
            status_code=500, detail="An unexpected server error occurred. Please try again later."
        ) from exc


@router.get("/health")
async def health_check() -> dict:
    """Simple health check endpoint used by Render and monitoring tools."""
    return {"status": "ok"}


@router.get("/debug-env")
async def debug_env() -> dict:
    """
    Diagnostic endpoint to confirm whether GROQ_API_KEY is loaded, without
    ever exposing the key's value. Visit /api/debug-env in the browser to
    quickly check configuration when troubleshooting a 401 error.
    """
    key = os.getenv("GROQ_API_KEY")
    return {
        "groq_api_key_loaded": bool(key),
        "groq_api_key_length": len(key) if key else 0,
        "groq_model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    }
