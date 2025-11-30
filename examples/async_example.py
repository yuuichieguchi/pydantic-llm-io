"""Async example with concurrent requests."""

import asyncio
import json

from pydantic import BaseModel, Field

from pydantic_llm_io import (
    FakeChatClient,
    LLMCallConfig,
    call_llm_validated_async,
)


class TranslationInput(BaseModel):
    """Input for translation."""

    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language")


class TranslationOutput(BaseModel):
    """Output for translation."""

    translated_text: str
    confidence: float = Field(..., ge=0.0, le=1.0)


async def translate_async(
    text: str,
    target_language: str,
    client_response: str,
) -> TranslationOutput:
    """Translate text asynchronously."""
    client = FakeChatClient(client_response)

    result = await call_llm_validated_async(
        prompt_model=TranslationInput(
            text=text,
            target_language=target_language,
        ),
        response_model=TranslationOutput,
        client=client,
        config=LLMCallConfig(),
    )

    return result


async def main() -> None:
    """Run async example with concurrent translations."""
    # Create mock responses for different languages
    spanish_response = json.dumps({
        "translated_text": "Hola mundo",
        "confidence": 0.95,
    })

    french_response = json.dumps({
        "translated_text": "Bonjour le monde",
        "confidence": 0.93,
    })

    german_response = json.dumps({
        "translated_text": "Hallo Welt",
        "confidence": 0.94,
    })

    # Execute translations concurrently
    results = await asyncio.gather(
        translate_async("Hello world", "Spanish", spanish_response),
        translate_async("Hello world", "French", french_response),
        translate_async("Hello world", "German", german_response),
    )

    # Display results
    languages = ["Spanish", "French", "German"]
    for lang, result in zip(languages, results):
        print(f"{lang}: {result.translated_text} (confidence: {result.confidence})")


if __name__ == "__main__":
    asyncio.run(main())
