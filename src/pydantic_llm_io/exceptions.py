"""Exception class definitions and error handling."""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class LLMIOError(Exception):
    """Base exception for all pydantic-llm-io errors."""

    def __init__(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            context: Error context (debug information)
        """
        self.message = message
        self.context = context or {}
        super().__init__(message)

    def __str__(self) -> str:
        """String representation."""
        return self.message

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "context": self.context,
        }


class LLMCallError(LLMIOError):
    """LLM API call failure error."""

    def __init__(
        self,
        message: str,
        provider: str,
        raw_error: Exception,
        attempt: int = 0,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            provider: Provider name ('openai', 'anthropic', etc.)
            raw_error: Original exception object
            attempt: Retry attempt number
        """
        context: dict[str, Any] = {
            "provider": provider,
            "raw_error": str(raw_error),
            "attempt": attempt,
        }
        super().__init__(message, context)
        logger.error(
            f"LLM call failed on provider '{provider}' (attempt {attempt + 1}): {message}",
            exc_info=raw_error,
        )


class LLMParseError(LLMIOError):
    """JSON parsing failure error."""

    def __init__(
        self,
        message: str,
        raw_response: str,
        parse_error: Exception,
        attempt: int = 0,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            raw_response: LLM response that failed to parse
            parse_error: JSON parsing error details
            attempt: Retry attempt number
        """
        context: dict[str, Any] = {
            "raw_response": raw_response[:1000],  # Length limit
            "parse_error": str(parse_error),
            "attempt": attempt,
        }
        super().__init__(message, context)
        logger.warning(
            f"JSON parsing failed (attempt {attempt + 1}): {message}",
            extra={"raw_response_preview": raw_response[:200]},
        )


class LLMValidationError(LLMIOError):
    """Pydantic validation failure error."""

    def __init__(
        self,
        message: str,
        raw_response: str,
        validation_errors: list[dict[str, Any]],
        attempt: int = 0,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            raw_response: LLM response that failed validation
            validation_errors: Pydantic validation error details
            attempt: Retry attempt number
        """
        context: dict[str, Any] = {
            "raw_response": raw_response[:1000],  # Length limit
            "validation_errors": validation_errors,
            "attempt": attempt,
        }
        super().__init__(message, context)
        error_count = len(validation_errors)
        logger.warning(
            f"Pydantic validation failed (attempt {attempt + 1}): {error_count} error(s)",
            extra={"errors": validation_errors[:3]},  # First 3 errors only
        )


class RetryExhaustedError(LLMIOError):
    """All retry attempts have been exhausted."""

    def __init__(
        self,
        message: str,
        last_error: LLMIOError,
        attempts: int,
    ) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            last_error: Last occurred error
            attempts: Number of attempts
        """
        context: dict[str, Any] = {
            "last_error": last_error.to_dict(),
            "attempts": attempts,
        }
        super().__init__(message, context)
        logger.error(
            f"Retry exhausted after {attempts} attempts. Last error: {last_error.message}"
        )


class ConfigError(LLMIOError):
    """Configuration error."""

    def __init__(self, message: str, config_key: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            config_key: Configuration key that caused the issue
        """
        context: dict[str, Any] = {}
        if config_key:
            context["config_key"] = config_key
        super().__init__(message, context)
