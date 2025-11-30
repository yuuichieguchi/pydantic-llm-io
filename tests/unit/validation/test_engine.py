"""Tests for validation engine."""

import asyncio
import json
import logging

import pytest
from pydantic import BaseModel

from pydantic_llm_io import (
    FakeChatClient,
    LLMParseError,
    LLMValidationError,
    LoggingConfig,
    RetryConfig,
    RetryExhaustedError,
)
from pydantic_llm_io.validation import ValidationEngine


class SampleModel(BaseModel):
    """Sample model for validation tests."""

    name: str
    value: int


class TestValidationEngine:
    """Test ValidationEngine."""

    def test_validate_success(self) -> None:
        """Test successful validation."""
        engine = ValidationEngine(
            retry_config=RetryConfig(),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        valid_json = json.dumps({"name": "test", "value": 42})
        result = engine.validate(valid_json, SampleModel)

        assert result.name == "test"
        assert result.value == 42

    def test_validate_invalid_json(self) -> None:
        """Test validation with invalid JSON."""
        engine = ValidationEngine(
            retry_config=RetryConfig(),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        with pytest.raises(LLMParseError):
            engine.validate('{"invalid": json}', SampleModel)

    def test_validate_invalid_schema(self) -> None:
        """Test validation with invalid schema."""
        engine = ValidationEngine(
            retry_config=RetryConfig(),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        invalid_json = json.dumps({"name": "test"})  # missing 'value'
        with pytest.raises(LLMValidationError):
            engine.validate(invalid_json, SampleModel)

    def test_validate_with_retries_success_first_try(self) -> None:
        """Test validate_with_retries succeeds on first attempt."""
        engine = ValidationEngine(
            retry_config=RetryConfig(initial_delay_seconds=0.001),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        valid_json = json.dumps({"name": "test", "value": 42})
        client = FakeChatClient(valid_json)

        result = engine.validate_with_retries(
            response_text=valid_json,
            response_model=SampleModel,
            client=client,
            prompt_system="sys",
            prompt_user="usr",
        )

        assert result.name == "test"
        assert client.call_count == 0  # No retry queries

    def test_validate_with_retries_after_error(self) -> None:
        """Test validate_with_retries succeeds after retry."""
        engine = ValidationEngine(
            retry_config=RetryConfig(
                max_retries=2,
                initial_delay_seconds=0.001,
            ),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        valid_json = json.dumps({"name": "test", "value": 42})
        client = FakeChatClient(valid_json)

        # First attempt fails, retry succeeds
        invalid_json = '{"invalid": json}'

        result = engine.validate_with_retries(
            response_text=invalid_json,
            response_model=SampleModel,
            client=client,
            prompt_system="sys",
            prompt_user="usr",
        )

        assert result.name == "test"
        assert client.call_count == 1  # One retry query

    def test_validate_with_retries_exhausted(self) -> None:
        """Test validate_with_retries after exhausting retries."""
        engine = ValidationEngine(
            retry_config=RetryConfig(
                max_retries=1,
                initial_delay_seconds=0.001,
            ),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        # Always return invalid JSON
        client = FakeChatClient('{"invalid": json}')

        with pytest.raises(RetryExhaustedError) as exc_info:
            engine.validate_with_retries(
                response_text='{"invalid": json}',
                response_model=SampleModel,
                client=client,
                prompt_system="sys",
                prompt_user="usr",
            )

        assert exc_info.value.context["attempts"] == 2  # max_retries + 1

    @pytest.mark.asyncio
    async def test_validate_with_retries_async_success(self) -> None:
        """Test async validation succeeds."""
        engine = ValidationEngine(
            retry_config=RetryConfig(initial_delay_seconds=0.001),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        valid_json = json.dumps({"name": "test", "value": 42})
        client = FakeChatClient(valid_json)

        result = await engine.validate_with_retries_async(
            response_text=valid_json,
            response_model=SampleModel,
            client=client,
            prompt_system="sys",
            prompt_user="usr",
        )

        assert result.name == "test"

    @pytest.mark.asyncio
    async def test_validate_with_retries_async_exhausted(self) -> None:
        """Test async validation exhaustion."""
        engine = ValidationEngine(
            retry_config=RetryConfig(
                max_retries=1,
                initial_delay_seconds=0.001,
            ),
            logging_config=LoggingConfig(),
            logger=logging.getLogger("test"),
        )

        client = FakeChatClient('{"invalid": json}')

        with pytest.raises(RetryExhaustedError):
            await engine.validate_with_retries_async(
                response_text='{"invalid": json}',
                response_model=SampleModel,
                client=client,
                prompt_system="sys",
                prompt_user="usr",
            )
