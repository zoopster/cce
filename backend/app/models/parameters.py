"""
Parameter models for content generation configuration.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Type of content to generate."""

    BLOG_POST = "blog_post"
    TECHNICAL_TUTORIAL = "technical_tutorial"
    MARKETING_CONTENT = "marketing_content"


class Tone(str, Enum):
    """Tone of voice for the content."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"


class AudienceLevel(str, Enum):
    """Target audience expertise level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    GENERAL = "general"


class GenerationParameters(BaseModel):
    """Parameters controlling content generation."""

    content_type: ContentType = ContentType.BLOG_POST
    tone: Tone = Tone.PROFESSIONAL
    audience_level: AudienceLevel = AudienceLevel.GENERAL
    word_count: int = Field(default=1500, ge=500, le=5000)
    keywords: List[str] = Field(default_factory=list)
    custom_instructions: Optional[str] = None
