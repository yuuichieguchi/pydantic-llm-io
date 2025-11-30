"""OpenAI API client implementation."""

from openai import AsyncOpenAI, OpenAI

from ..exceptions import LLMCallError
from .base import ChatClient


class OpenAIChatClient(ChatClient):
    """OpenAI API implementation of ChatClient."""

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o)
        """
        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model = model

    def send_message(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
    ) -> str:
        """Send message to OpenAI API.

        Args:
            system: System prompt
            user: User message
            temperature: Sampling temperature

        Returns:
            Response text

        Raises:
            LLMCallError: If API request fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
            )
            content = response.choices[0].message.content
            if content is None:
                raise LLMCallError(
                    message="OpenAI returned empty response content",
                    provider="openai",
                    raw_error=ValueError("Empty content"),
                    attempt=0,
                )
            return content
        except Exception as e:
            raise LLMCallError(
                message=f"OpenAI API request failed: {str(e)}",
                provider="openai",
                raw_error=e,
                attempt=0,
            )

    async def send_message_async(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
    ) -> str:
        """Send message to OpenAI API (async).

        Args:
            system: System prompt
            user: User message
            temperature: Sampling temperature

        Returns:
            Response text

        Raises:
            LLMCallError: If API request fails
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
            )
            content = response.choices[0].message.content
            if content is None:
                raise LLMCallError(
                    message="OpenAI returned empty response content",
                    provider="openai",
                    raw_error=ValueError("Empty content"),
                    attempt=0,
                )
            return content
        except Exception as e:
            raise LLMCallError(
                message=f"OpenAI API request failed: {str(e)}",
                provider="openai",
                raw_error=e,
                attempt=0,
            )

    def get_provider_name(self) -> str:
        """Get provider name.

        Returns:
            Provider name 'openai'
        """
        return "openai"
