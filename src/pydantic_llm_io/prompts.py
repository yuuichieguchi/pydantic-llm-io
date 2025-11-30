"""Prompt construction and management."""

import json
from typing import Any

from pydantic import BaseModel

from .types import PromptModelT, ResponseModelT


DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that responds with valid JSON only.
Respond ONLY with valid JSON matching the specified schema. No markdown, no code blocks, no explanations."""


class PromptBuilder:
    """Constructs system and user messages from Pydantic models."""

    def __init__(self, custom_system_prompt: str | None = None) -> None:
        """Initialize the prompt builder.

        Args:
            custom_system_prompt: Custom system prompt to override default
        """
        self.system_prompt = custom_system_prompt or DEFAULT_SYSTEM_PROMPT

    def build(
        self,
        prompt_model: PromptModelT,
        response_model_schema: dict[str, Any],
    ) -> tuple[str, str]:
        """Build system and user messages.

        Args:
            prompt_model: Pydantic model containing user prompt
            response_model_schema: JSON schema for expected response

        Returns:
            Tuple of (system_message, user_message)
        """
        system = self._build_system(response_model_schema)
        user = self._build_user(prompt_model)
        return system, user

    def _build_system(self, schema: dict[str, Any]) -> str:
        """Build system prompt with schema.

        Args:
            schema: JSON schema for response validation

        Returns:
            System prompt string
        """
        schema_str = json.dumps(schema, indent=2)
        return f"""{self.system_prompt}

Expected JSON schema:
```json
{schema_str}
```"""

    def _build_user(self, prompt_model: BaseModel) -> str:
        """Build user message from prompt model.

        Args:
            prompt_model: Pydantic model instance

        Returns:
            User message string
        """
        return prompt_model.model_dump_json(indent=2)
