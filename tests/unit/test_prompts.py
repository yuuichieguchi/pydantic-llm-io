"""Tests for prompt building."""

import pytest
from pydantic import BaseModel

from pydantic_llm_io.prompts import DEFAULT_SYSTEM_PROMPT, PromptBuilder


class SamplePrompt(BaseModel):
    """Sample prompt model."""

    text: str
    max_tokens: int


class SampleResponse(BaseModel):
    """Sample response model."""

    result: str


class TestPromptBuilder:
    """Test PromptBuilder."""

    def test_default_system_prompt(self) -> None:
        """Test default system prompt."""
        builder = PromptBuilder()
        assert builder.system_prompt == DEFAULT_SYSTEM_PROMPT
        assert "JSON" in builder.system_prompt

    def test_custom_system_prompt(self) -> None:
        """Test custom system prompt."""
        custom = "You are a custom AI."
        builder = PromptBuilder(custom_system_prompt=custom)
        assert builder.system_prompt == custom

    def test_build_messages(self) -> None:
        """Test building system and user messages."""
        builder = PromptBuilder()
        prompt = SamplePrompt(text="Hello", max_tokens=100)
        schema = SampleResponse.model_json_schema()

        system, user = builder.build(prompt, schema)

        # System should contain default prompt and schema
        assert DEFAULT_SYSTEM_PROMPT in system
        assert "SampleResponse" in system
        assert "properties" in system

        # User should contain prompt JSON
        assert '"text"' in user
        assert '"Hello"' in user
        assert '"max_tokens"' in user

    def test_build_user_message(self) -> None:
        """Test user message construction."""
        builder = PromptBuilder()
        prompt = SamplePrompt(text="Test text", max_tokens=50)

        user_msg = builder._build_user(prompt)

        assert isinstance(user_msg, str)
        assert "Test text" in user_msg
        assert "50" in user_msg

    def test_build_system_message(self) -> None:
        """Test system message construction."""
        builder = PromptBuilder(custom_system_prompt="Custom: ")
        schema = {"type": "object", "properties": {"key": {"type": "string"}}}

        system_msg = builder._build_system(schema)

        assert "Custom: " in system_msg
        assert "Expected JSON schema" in system_msg
        assert "key" in system_msg

    def test_schema_in_system_prompt(self) -> None:
        """Test that schema is properly formatted in system prompt."""
        builder = PromptBuilder()
        schema = SampleResponse.model_json_schema()

        system, _ = builder.build(SamplePrompt(text="x", max_tokens=1), schema)

        # Check for JSON code block formatting
        assert "```json" in system
        assert "```" in system
