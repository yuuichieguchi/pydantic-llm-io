"""Pytest configuration and fixtures."""

import json
import logging

import pytest
from pydantic import BaseModel

from pydantic_llm_io import FakeChatClient, LLMCallConfig, LoggingConfig, RetryConfig


# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


class TestPromptModel(BaseModel):
    """Test prompt model."""

    text: str
    max_words: int = 100


class TestResponseModel(BaseModel):
    """Test response model."""

    summary: str
    key_points: list[str]
    language: str


@pytest.fixture
def test_prompt() -> TestPromptModel:
    """Create a test prompt model."""
    return TestPromptModel(text="Sample text to summarize", max_words=50)


@pytest.fixture
def test_response_dict() -> dict:
    """Create a valid response dictionary."""
    return {
        "summary": "This is a summary",
        "key_points": ["point 1", "point 2"],
        "language": "English",
    }


@pytest.fixture
def test_response_json(test_response_dict: dict) -> str:
    """Create a valid JSON response."""
    return json.dumps(test_response_dict)


@pytest.fixture
def fake_client(test_response_json: str) -> FakeChatClient:
    """Create a fake chat client with valid response."""
    return FakeChatClient(test_response_json)


@pytest.fixture
def test_config() -> LLMCallConfig:
    """Create a test config with minimal retries."""
    return LLMCallConfig(
        retry=RetryConfig(max_retries=2, initial_delay_seconds=0.01),
        logging=LoggingConfig(level="DEBUG"),
    )
