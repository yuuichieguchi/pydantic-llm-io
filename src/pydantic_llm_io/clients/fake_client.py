"""Fake chat client for testing."""

from .base import ChatClient


class FakeChatClient(ChatClient):
    """Testing double that returns predefined responses."""

    def __init__(self, response_text: str) -> None:
        """Initialize fake client.

        Args:
            response_text: Fixed response to return
        """
        self.response_text = response_text
        self.call_count = 0
        self.last_system: str | None = None
        self.last_user: str | None = None
        self.call_history: list[dict[str, str]] = []

    def send_message(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
    ) -> str:
        """Return predefined response (sync).

        Args:
            system: System prompt (recorded but not used)
            user: User message (recorded but not used)
            temperature: Temperature (recorded but not used)

        Returns:
            Predefined response text
        """
        self.call_count += 1
        self.last_system = system
        self.last_user = user
        self.call_history.append({
            "system": system,
            "user": user,
            "temperature": str(temperature),
        })
        return self.response_text

    async def send_message_async(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
    ) -> str:
        """Return predefined response (async).

        Args:
            system: System prompt (recorded but not used)
            user: User message (recorded but not used)
            temperature: Temperature (recorded but not used)

        Returns:
            Predefined response text
        """
        return self.send_message(system, user, temperature)

    def get_provider_name(self) -> str:
        """Get provider name.

        Returns:
            Provider name 'fake'
        """
        return "fake"

    def reset(self) -> None:
        """Reset call history."""
        self.call_count = 0
        self.last_system = None
        self.last_user = None
        self.call_history.clear()
