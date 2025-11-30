"""pydantic-llm-io: Type-safe, validated input/output handling for LLM calls."""

__version__ = "1.0.1"

from .api import call_llm_validated, call_llm_validated_async
from .clients import ChatClient, FakeChatClient, OpenAIChatClient
from .config import LLMCallConfig, LoggingConfig, RetryConfig
from .exceptions import (
    ConfigError,
    LLMCallError,
    LLMIOError,
    LLMParseError,
    LLMValidationError,
    RetryExhaustedError,
)

__all__ = [
    # API
    "call_llm_validated",
    "call_llm_validated_async",
    # Clients
    "ChatClient",
    "OpenAIChatClient",
    "FakeChatClient",
    # Config
    "LLMCallConfig",
    "LoggingConfig",
    "RetryConfig",
    # Exceptions
    "LLMIOError",
    "LLMCallError",
    "LLMParseError",
    "LLMValidationError",
    "RetryExhaustedError",
    "ConfigError",
]
