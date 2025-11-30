"""Type definitions and generic constraints."""

from enum import Enum
from typing import TypeVar

from pydantic import BaseModel

# Generic type variables
PromptModelT = TypeVar("PromptModelT", bound=BaseModel)
ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class MessageRole(str, Enum):
    """Message role definition."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ProviderType(str, Enum):
    """LLM provider types."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    CUSTOM = "custom"
