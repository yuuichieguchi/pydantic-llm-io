"""Tests for exception classes."""

import pytest

from pydantic_llm_io import (
    ConfigError,
    LLMCallError,
    LLMIOError,
    LLMParseError,
    LLMValidationError,
    RetryExhaustedError,
)


class TestLLMIOError:
    """Test base LLMIOError."""

    def test_error_creation(self) -> None:
        """Test creating base error."""
        error = LLMIOError("Test error message")
        assert error.message == "Test error message"
        assert error.context == {}
        assert str(error) == "Test error message"

    def test_error_with_context(self) -> None:
        """Test error with context."""
        context = {"key": "value", "count": 42}
        error = LLMIOError("Test error", context=context)
        assert error.context == context

    def test_error_to_dict(self) -> None:
        """Test error serialization to dict."""
        error = LLMIOError("Test error", context={"info": "data"})
        error_dict = error.to_dict()
        assert error_dict["error"] == "LLMIOError"
        assert error_dict["message"] == "Test error"
        assert error_dict["context"] == {"info": "data"}


class TestLLMCallError:
    """Test LLMCallError."""

    def test_llm_call_error_creation(self) -> None:
        """Test creating LLM call error."""
        raw_error = ValueError("API error")
        error = LLMCallError(
            message="API request failed",
            provider="openai",
            raw_error=raw_error,
            attempt=0,
        )
        assert error.message == "API request failed"
        assert error.context["provider"] == "openai"
        assert error.context["attempt"] == 0
        assert "API error" in error.context["raw_error"]


class TestLLMParseError:
    """Test LLMParseError."""

    def test_parse_error_creation(self) -> None:
        """Test creating parse error."""
        raw_resp = '{"invalid": json}'
        parse_err = ValueError("Unterminated string")
        error = LLMParseError(
            message="JSON parsing failed",
            raw_response=raw_resp,
            parse_error=parse_err,
            attempt=1,
        )
        assert error.message == "JSON parsing failed"
        assert error.context["attempt"] == 1
        assert raw_resp in error.context["raw_response"]

    def test_parse_error_response_truncation(self) -> None:
        """Test that long responses are truncated."""
        long_response = "x" * 2000
        error = LLMParseError(
            message="Parse failed",
            raw_response=long_response,
            parse_error=ValueError("Error"),
            attempt=0,
        )
        # Should be truncated to 1000 chars
        assert len(error.context["raw_response"]) <= 1000


class TestLLMValidationError:
    """Test LLMValidationError."""

    def test_validation_error_creation(self) -> None:
        """Test creating validation error."""
        validation_errors = [
            {"loc": ("summary",), "msg": "field required", "type": "value_error"}
        ]
        error = LLMValidationError(
            message="Validation failed: 1 error(s)",
            raw_response='{"key_points": []}',
            validation_errors=validation_errors,
            attempt=2,
        )
        assert error.message == "Validation failed: 1 error(s)"
        assert error.context["attempt"] == 2
        assert error.context["validation_errors"] == validation_errors


class TestRetryExhaustedError:
    """Test RetryExhaustedError."""

    def test_retry_exhausted_error(self) -> None:
        """Test creating retry exhausted error."""
        last_error = LLMParseError(
            message="Parse failed",
            raw_response="bad json",
            parse_error=ValueError("Error"),
            attempt=2,
        )
        error = RetryExhaustedError(
            message="All retries failed",
            last_error=last_error,
            attempts=3,
        )
        assert error.message == "All retries failed"
        assert error.context["attempts"] == 3
        assert error.context["last_error"]["error"] == "LLMParseError"


class TestConfigError:
    """Test ConfigError."""

    def test_config_error_creation(self) -> None:
        """Test creating config error."""
        error = ConfigError("Invalid config", config_key="api_key")
        assert error.message == "Invalid config"
        assert error.context["config_key"] == "api_key"

    def test_config_error_without_key(self) -> None:
        """Test config error without key."""
        error = ConfigError("Invalid config")
        assert "config_key" not in error.context
