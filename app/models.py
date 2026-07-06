"""
Pydantic models for request/response validation.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class ToneEnum(str, Enum):
    """Allowed tone options for the generated post."""

    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    INSPIRATIONAL = "Inspirational"
    TECHNICAL = "Technical"
    MARKETING = "Marketing"
    EDUCATIONAL = "Educational"


class LengthEnum(str, Enum):
    """Allowed length options for the generated post."""

    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"


class GoalEnum(str, Enum):
    """Allowed goal options for the generated post."""

    PERSONAL_BRANDING = "Personal Branding"
    HIRING = "Hiring"
    PRODUCT_LAUNCH = "Product Launch"
    ACHIEVEMENT = "Achievement"
    LEARNING = "Learning"
    NETWORKING = "Networking"
    ANNOUNCEMENT = "Announcement"


class PostRequest(BaseModel):
    """Input payload for the /generate endpoint."""

    topic: str = Field(..., min_length=2, max_length=300, description="Topic of the post")
    audience: str = Field(..., min_length=2, max_length=200, description="Target audience")
    tone: ToneEnum = Field(..., description="Tone of the post")
    length: LengthEnum = Field(..., description="Desired length of the post")
    goal: GoalEnum = Field(..., description="Goal of the post")
    keywords: Optional[str] = Field(default="", max_length=300, description="Optional keywords")

    @field_validator("topic", "audience")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Ensure required text fields are not just whitespace."""
        if not value or not value.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return value.strip()

    @field_validator("keywords")
    @classmethod
    def clean_keywords(cls, value: Optional[str]) -> str:
        """Normalize optional keywords field."""
        return value.strip() if value else ""


class PostResponse(BaseModel):
    """Final structured output returned to the client."""

    hook: str
    post: str
    hashtags: List[str]


class ErrorResponse(BaseModel):
    """Standard error payload."""

    error: str
    detail: Optional[str] = None
