"""Tests for FakeChatClient."""

import pytest

from pydantic_llm_io import FakeChatClient


class TestFakeChatClient:
    """Test FakeChatClient implementation."""

    def test_fake_client_returns_predefined_response(self) -> None:
        """Test that fake client returns predefined response."""
        response = '{"key": "value"}'
        client = FakeChatClient(response)

        result = client.send_message(system="sys", user="usr")
        assert result == response

    def test_fake_client_tracks_calls(self) -> None:
        """Test that fake client tracks function calls."""
        client = FakeChatClient('{"data": "test"}')

        client.send_message(system="system prompt", user="user prompt")
        assert client.call_count == 1
        assert client.last_system == "system prompt"
        assert client.last_user == "user prompt"

    def test_fake_client_call_history(self) -> None:
        """Test call history tracking."""
        client = FakeChatClient("response")

        client.send_message(system="sys1", user="usr1", temperature=0.5)
        client.send_message(system="sys2", user="usr2", temperature=0.8)

        assert client.call_count == 2
        assert len(client.call_history) == 2
        assert client.call_history[0]["system"] == "sys1"
        assert client.call_history[1]["user"] == "usr2"

    def test_fake_client_async(self) -> None:
        """Test async method."""
        import asyncio

        client = FakeChatClient("async response")

        async def test() -> str:
            return await client.send_message_async(system="s", user="u")

        result = asyncio.run(test())
        assert result == "async response"

    def test_fake_client_reset(self) -> None:
        """Test reset functionality."""
        client = FakeChatClient("response")

        client.send_message(system="s", user="u")
        assert client.call_count == 1

        client.reset()
        assert client.call_count == 0
        assert client.last_system is None
        assert client.last_user is None
        assert len(client.call_history) == 0

    def test_fake_client_provider_name(self) -> None:
        """Test provider name."""
        client = FakeChatClient("response")
        assert client.get_provider_name() == "fake"
