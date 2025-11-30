"""Validation engine with retry logic."""

import asyncio
import json
import logging
import time
from typing import Any

from pydantic import BaseModel, ValidationError as PydanticValidationError

from ..clients.base import ChatClient
from ..config import LoggingConfig, RetryConfig
from ..exceptions import (
    LLMParseError,
    LLMValidationError,
    RetryExhaustedError,
)
from ..types import ResponseModelT


class ValidationEngine:
    """Handles JSON parsing and Pydantic validation with retries."""

    def __init__(
        self,
        retry_config: RetryConfig,
        logging_config: LoggingConfig,
        logger: logging.Logger,
    ) -> None:
        """Initialize validation engine.

        Args:
            retry_config: Retry configuration
            logging_config: Logging configuration
            logger: Logger instance
        """
        self.retry_config = retry_config
        self.logging_config = logging_config
        self.logger = logger

    def validate(
        self,
        raw_response: str,
        response_model: type[ResponseModelT],
    ) -> ResponseModelT:
        """Validate response without retries.

        Args:
            raw_response: Raw LLM response text
            response_model: Pydantic model for validation

        Returns:
            Validated response model instance

        Raises:
            LLMParseError: If JSON parsing fails
            LLMValidationError: If Pydantic validation fails
        """
        # Parse JSON
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as e:
            raise LLMParseError(
                message=f"JSON parsing failed: {str(e)}",
                raw_response=raw_response,
                parse_error=e,
                attempt=0,
            )

        # Validate Pydantic
        try:
            return response_model.model_validate(data)
        except PydanticValidationError as e:
            raise LLMValidationError(
                message=f"Pydantic validation failed: {e.error_count()} error(s)",
                raw_response=raw_response,
                validation_errors=e.errors(),
                attempt=0,
            )

    def validate_with_retries(
        self,
        response_text: str,
        response_model: type[ResponseModelT],
        client: ChatClient,
        prompt_system: str,
        prompt_user: str,
    ) -> ResponseModelT:
        """Validate response with retries and LLM re-querying.

        Args:
            response_text: Initial response text from LLM
            response_model: Pydantic model for validation
            client: Chat client for retry queries
            prompt_system: System prompt (for re-query)
            prompt_user: User prompt (for re-query)

        Returns:
            Validated response model instance

        Raises:
            LLMParseError: If JSON parsing consistently fails
            LLMValidationError: If validation consistently fails
            RetryExhaustedError: If all retries are exhausted
        """
        last_error: Any = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return self.validate(response_text, response_model)
            except (LLMParseError, LLMValidationError) as e:
                last_error = e
                self._log_validation_failure(e, attempt)

                # If retries remain, ask LLM to correct
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    time.sleep(delay)

                    # Build correction prompt
                    correction_prompt = self._build_correction_prompt(e, attempt)
                    try:
                        response_text = client.send_message(
                            system=prompt_system,
                            user=correction_prompt,
                        )
                    except Exception as retry_error:
                        self.logger.warning(
                            f"Retry query failed on attempt {attempt + 1}: {str(retry_error)}"
                        )
                        # Continue to next retry or fail

        # All retries exhausted
        assert last_error is not None
        raise RetryExhaustedError(
            message=f"Validation failed after {self.retry_config.max_retries + 1} attempts",
            last_error=last_error,
            attempts=self.retry_config.max_retries + 1,
        )

    async def validate_with_retries_async(
        self,
        response_text: str,
        response_model: type[ResponseModelT],
        client: ChatClient,
        prompt_system: str,
        prompt_user: str,
    ) -> ResponseModelT:
        """Async version of validate_with_retries.

        Args:
            response_text: Initial response text from LLM
            response_model: Pydantic model for validation
            client: Chat client for retry queries
            prompt_system: System prompt (for re-query)
            prompt_user: User prompt (for re-query)

        Returns:
            Validated response model instance

        Raises:
            LLMParseError: If JSON parsing consistently fails
            LLMValidationError: If validation consistently fails
            RetryExhaustedError: If all retries are exhausted
        """
        last_error: Any = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return self.validate(response_text, response_model)
            except (LLMParseError, LLMValidationError) as e:
                last_error = e
                self._log_validation_failure(e, attempt)

                # If retries remain, ask LLM to correct
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    await asyncio.sleep(delay)

                    # Build correction prompt
                    correction_prompt = self._build_correction_prompt(e, attempt)
                    try:
                        response_text = await client.send_message_async(
                            system=prompt_system,
                            user=correction_prompt,
                        )
                    except Exception as retry_error:
                        self.logger.warning(
                            f"Retry query failed on attempt {attempt + 1}: {str(retry_error)}"
                        )
                        # Continue to next retry or fail

        # All retries exhausted
        assert last_error is not None
        raise RetryExhaustedError(
            message=f"Validation failed after {self.retry_config.max_retries + 1} attempts",
            last_error=last_error,
            attempts=self.retry_config.max_retries + 1,
        )

    def _build_correction_prompt(self, error: LLMParseError | LLMValidationError, attempt: int) -> str:
        """Build a follow-up prompt with validation error details.

        Args:
            error: Validation error with details
            attempt: Current attempt number

        Returns:
            Correction prompt string
        """
        error_details = error.context.get("validation_errors") or error.context.get("parse_error")
        raw_response = error.context.get("raw_response", "")[:500]

        return f"""Your previous response was invalid (attempt {attempt + 1}).

Error details:
{json.dumps({"error": error_details}, indent=2)}

Your previous response:
{raw_response}

Please provide a corrected JSON response that strictly adheres to the schema."""

    def _log_validation_failure(
        self,
        error: LLMParseError | LLMValidationError,
        attempt: int,
    ) -> None:
        """Log validation failure with appropriate detail level.

        Args:
            error: Validation error
            attempt: Attempt number
        """
        msg = f"Validation failed (attempt {attempt + 1}/{self.retry_config.max_retries + 1})"

        if self.logging_config.include_raw_response:
            raw = error.context.get("raw_response", "N/A")[:300]
            msg += f"\n  Raw response: {raw}"

        if self.logging_config.include_validation_errors:
            if isinstance(error, LLMValidationError):
                errors = error.context.get("validation_errors", [])[:2]
                msg += f"\n  Validation errors: {errors}"
            elif isinstance(error, LLMParseError):
                parse_err = error.context.get("parse_error", "Unknown")
                msg += f"\n  Parse error: {parse_err}"

        self.logger.warning(msg)
