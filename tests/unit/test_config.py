"""Tests for configuration module."""

import pytest

from pydantic_llm_io import ConfigError, LoggingConfig, LLMCallConfig, RetryConfig


class TestRetryConfig:
    """Test RetryConfig dataclass."""

    def test_default_retry_config(self) -> None:
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.initial_delay_seconds == 1.0
        assert config.backoff_multiplier == 2.0

    def test_exponential_backoff(self) -> None:
        """Test exponential backoff calculation."""
        config = RetryConfig(
            max_retries=3,
            initial_delay_seconds=1.0,
            backoff_multiplier=2.0,
        )
        assert config.get_delay(0) == 1.0  # 1 * 2^0
        assert config.get_delay(1) == 2.0  # 1 * 2^1
        assert config.get_delay(2) == 4.0  # 1 * 2^2

    def test_retry_config_validation(self) -> None:
        """Test RetryConfig validation."""
        with pytest.raises(ValueError, match="max_retries must be >= 0"):
            RetryConfig(max_retries=-1)

        with pytest.raises(ValueError, match="initial_delay_seconds must be >= 0"):
            RetryConfig(initial_delay_seconds=-1)

        with pytest.raises(ValueError, match="backoff_multiplier must be > 1"):
            RetryConfig(backoff_multiplier=1.0)

    def test_retry_config_immutable(self) -> None:
        """Test that RetryConfig is immutable."""
        config = RetryConfig()
        with pytest.raises(AttributeError):
            config.max_retries = 5  # type: ignore


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""

    def test_default_logging_config(self) -> None:
        """Test default logging configuration."""
        config = LoggingConfig()
        assert config.level == "INFO"
        assert config.include_raw_response is True
        assert config.include_validation_errors is True

    def test_logging_level_conversion(self) -> None:
        """Test logging level string to int conversion."""
        config_debug = LoggingConfig(level="DEBUG")
        config_error = LoggingConfig(level="ERROR")

        import logging

        assert config_debug.get_logging_level() == logging.DEBUG
        assert config_error.get_logging_level() == logging.ERROR

    def test_logging_config_validation(self) -> None:
        """Test LoggingConfig validation."""
        with pytest.raises(ValueError, match="level must be one of"):
            LoggingConfig(level="INVALID")

    def test_logging_config_immutable(self) -> None:
        """Test that LoggingConfig is immutable."""
        config = LoggingConfig()
        with pytest.raises(AttributeError):
            config.level = "DEBUG"  # type: ignore


class TestLLMCallConfig:
    """Test LLMCallConfig dataclass."""

    def test_default_llm_call_config(self) -> None:
        """Test default LLM call configuration."""
        config = LLMCallConfig()
        assert config.temperature == 0.7
        assert config.custom_system_prompt is None
        assert isinstance(config.retry, RetryConfig)
        assert isinstance(config.logging, LoggingConfig)

    def test_temperature_validation(self) -> None:
        """Test temperature validation."""
        # Valid range: 0-2
        LLMCallConfig(temperature=0.0)
        LLMCallConfig(temperature=1.0)
        LLMCallConfig(temperature=2.0)

        with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
            LLMCallConfig(temperature=-0.1)

        with pytest.raises(ValueError, match="temperature must be between 0 and 2"):
            LLMCallConfig(temperature=2.1)

    def test_custom_system_prompt(self) -> None:
        """Test custom system prompt."""
        custom_prompt = "You are a JSON expert."
        config = LLMCallConfig(custom_system_prompt=custom_prompt)
        assert config.custom_system_prompt == custom_prompt

    def test_llm_call_config_immutable(self) -> None:
        """Test that LLMCallConfig is immutable."""
        config = LLMCallConfig()
        with pytest.raises(AttributeError):
            config.temperature = 1.5  # type: ignore
