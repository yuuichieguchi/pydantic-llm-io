"""Integration tests for main API."""

import json

import pytest
from pydantic import BaseModel

from pydantic_llm_io import (
    FakeChatClient,
    LLMCallConfig,
    LoggingConfig,
    RetryConfig,
    RetryExhaustedError,
    call_llm_validated,
    call_llm_validated_async,
)


class SummaryInput(BaseModel):
    """Input model for summarization."""

    text: str
    max_words: int


class SummaryOutput(BaseModel):
    """Output model for summarization."""

    summary: str
    key_points: list[str]
    language: str


class TestCallLLMValidated:
    """Test call_llm_validated function."""

    def test_successful_call(self) -> None:
        """Test successful LLM call with validation."""
        response_data = {
            "summary": "Brief summary",
            "key_points": ["point1", "point2"],
            "language": "English",
        }
        client = FakeChatClient(json.dumps(response_data))

        result = call_llm_validated(
            prompt_model=SummaryInput(text="Long text", max_words=50),
            response_model=SummaryOutput,
            client=client,
            config=LLMCallConfig(
                logging=LoggingConfig(level="WARNING")
            ),
        )

        assert result.summary == "Brief summary"
        assert result.language == "English"
        assert len(result.key_points) == 2

    def test_invalid_json_retry(self) -> None:
        """Test handling of invalid JSON with retry."""
        valid_response = json.dumps({
            "summary": "Fixed",
            "key_points": ["a"],
            "language": "en",
        })

        # First call returns invalid JSON, second call returns valid
        responses = ['{"invalid": json}', valid_response]
        response_index = [0]

        class RetryingClient(FakeChatClient):
            def send_message(self, system: str, user: str, temperature: float = 0.7) -> str:
                idx = response_index[0]
                response_index[0] += 1
                result = responses[idx] if idx < len(responses) else valid_response
                # Track call for retry query
                if idx > 0:
                    self.call_count += 1
                return result

        client = RetryingClient(valid_response)
        client.call_count = 0  # Reset to track only retry queries

        result = call_llm_validated(
            prompt_model=SummaryInput(text="text", max_words=10),
            response_model=SummaryOutput,
            client=client,
            config=LLMCallConfig(
                retry=RetryConfig(max_retries=1, initial_delay_seconds=0.001),
                logging=LoggingConfig(level="WARNING"),
            ),
        )

        assert result.summary == "Fixed"
        assert client.call_count == 1  # One retry query was made

    def test_validation_failure_after_retries(self) -> None:
        """Test validation failure after exhausting retries."""
        client = FakeChatClient('{"invalid": json}')

        with pytest.raises(RetryExhaustedError):
            call_llm_validated(
                prompt_model=SummaryInput(text="text", max_words=10),
                response_model=SummaryOutput,
                client=client,
                config=LLMCallConfig(
                    retry=RetryConfig(max_retries=1, initial_delay_seconds=0.001),
                    logging=LoggingConfig(level="WARNING"),
                ),
            )

    def test_with_custom_system_prompt(self) -> None:
        """Test with custom system prompt."""
        response_data = {
            "summary": "Summary",
            "key_points": ["a"],
            "language": "en",
        }
        client = FakeChatClient(json.dumps(response_data))

        custom_prompt = "You are an expert summarizer."

        result = call_llm_validated(
            prompt_model=SummaryInput(text="text", max_words=10),
            response_model=SummaryOutput,
            client=client,
            config=LLMCallConfig(
                custom_system_prompt=custom_prompt,
                logging=LoggingConfig(level="WARNING"),
            ),
        )

        # Check that custom prompt was passed to client
        assert client.last_system is not None
        assert custom_prompt in client.last_system
        assert result.summary == "Summary"

    def test_prompt_json_in_message(self) -> None:
        """Test that prompt model is serialized to JSON."""
        response_data = {
            "summary": "Sum",
            "key_points": ["x"],
            "language": "en",
        }
        client = FakeChatClient(json.dumps(response_data))

        input_model = SummaryInput(text="My text", max_words=50)

        call_llm_validated(
            prompt_model=input_model,
            response_model=SummaryOutput,
            client=client,
            config=LLMCallConfig(logging=LoggingConfig(level="WARNING")),
        )

        # Check that user message contains prompt data
        assert client.last_user is not None
        assert "My text" in client.last_user
        assert "50" in client.last_user


@pytest.mark.asyncio
async def test_call_llm_validated_async() -> None:
    """Test async version of call_llm_validated."""
    response_data = {
        "summary": "Async summary",
        "key_points": ["async"],
        "language": "en",
    }
    client = FakeChatClient(json.dumps(response_data))

    result = await call_llm_validated_async(
        prompt_model=SummaryInput(text="text", max_words=10),
        response_model=SummaryOutput,
        client=client,
        config=LLMCallConfig(logging=LoggingConfig(level="WARNING")),
    )

    assert result.summary == "Async summary"
    assert isinstance(result, SummaryOutput)


@pytest.mark.asyncio
async def test_async_retry() -> None:
    """Test async retry logic."""
    valid_response = json.dumps({
        "summary": "Fixed",
        "key_points": ["a"],
        "language": "en",
    })

    responses = ['{"invalid": json}', valid_response]
    response_index = [0]

    class AsyncRetryingClient(FakeChatClient):
        async def send_message_async(
            self, system: str, user: str, temperature: float = 0.7
        ) -> str:
            idx = response_index[0]
            response_index[0] += 1
            result = responses[idx] if idx < len(responses) else valid_response
            # Track call for retry query
            if idx > 0:
                self.call_count += 1
            return result

    client = AsyncRetryingClient(valid_response)
    client.call_count = 0  # Reset to track only retry queries

    result = await call_llm_validated_async(
        prompt_model=SummaryInput(text="text", max_words=10),
        response_model=SummaryOutput,
        client=client,
        config=LLMCallConfig(
            retry=RetryConfig(max_retries=1, initial_delay_seconds=0.001),
            logging=LoggingConfig(level="WARNING"),
        ),
    )

    assert result.summary == "Fixed"
    assert client.call_count == 1  # One retry query
