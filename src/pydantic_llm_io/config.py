"""Configuration management (immutable dataclasses)."""

import logging
from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetryConfig:
    """Retry configuration."""

    max_retries: int = 3
    initial_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0

    def __post_init__(self) -> None:
        """Validation."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.initial_delay_seconds < 0:
            raise ValueError("initial_delay_seconds must be >= 0")
        if self.backoff_multiplier <= 1:
            raise ValueError("backoff_multiplier must be > 1")

    def get_delay(self, attempt: int) -> float:
        """Get delay for a given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        return self.initial_delay_seconds * (self.backoff_multiplier ** attempt)


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    include_raw_response: bool = True
    include_validation_errors: bool = True

    def __post_init__(self) -> None:
        """Validation."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level.upper() not in valid_levels:
            raise ValueError(f"level must be one of {valid_levels}")

    def get_logging_level(self) -> int:
        """Return logging level as logging module constant."""
        return getattr(logging, self.level.upper())


@dataclass(frozen=True)
class LLMCallConfig:
    """LLM call configuration."""

    retry: RetryConfig = field(default_factory=RetryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    custom_system_prompt: str | None = None
    temperature: float = 0.7

    def __post_init__(self) -> None:
        """Validation."""
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
