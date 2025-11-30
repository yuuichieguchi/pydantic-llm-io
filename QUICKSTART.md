# pydantic-llm-io Quick Start Guide

## Installation

```bash
pip install pydantic-llm-io
```

## 5-Minute Tutorial

### Step 1: Define Your Models

```python
from pydantic import BaseModel, Field

class SummaryRequest(BaseModel):
    """What we send to the LLM."""
    article_text: str = Field(..., description="Full article to summarize")
    max_words: int = Field(100, description="Maximum summary length")

class SummaryResponse(BaseModel):
    """What we expect back from the LLM."""
    summary: str = Field(..., description="Concise summary")
    key_points: list[str] = Field(..., description="Main points")
```

### Step 2: Initialize a Client

```python
from pydantic_llm_io import OpenAIChatClient
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAIChatClient(api_key=api_key)
```

### Step 3: Call the LLM with Validation

```python
from pydantic_llm_io import call_llm_validated

result = call_llm_validated(
    prompt_model=SummaryRequest(
        article_text="Long article text here...",
        max_words=50
    ),
    response_model=SummaryResponse,
    client=client,
)

# Result is fully typed and validated
print(f"Summary: {result.summary}")
print(f"Key points: {result.key_points}")
```

That's it! The library automatically:
✅ Serializes your input to JSON
✅ Injects the output schema into the system prompt
✅ Calls OpenAI API
✅ Parses and validates the JSON response
✅ Retries if validation fails

## Testing Without API Calls

```python
from pydantic_llm_io import FakeChatClient
import json

# Create a fake client with a predefined response
fake_response = json.dumps({
    "summary": "Article summary here",
    "key_points": ["point 1", "point 2"]
})

client = FakeChatClient(fake_response)

# Use it exactly like the real client
result = call_llm_validated(
    prompt_model=SummaryRequest(...),
    response_model=SummaryResponse,
    client=client,  # Swap in fake client
)
```

## Configuration

### Customize Retries

```python
from pydantic_llm_io import LLMCallConfig, RetryConfig

config = LLMCallConfig(
    retry=RetryConfig(
        max_retries=3,              # Retry up to 3 times
        initial_delay_seconds=1.0,  # Wait 1 second before first retry
        backoff_multiplier=2.0,     # Double wait time each retry
    )
)

result = call_llm_validated(
    prompt_model=input_model,
    response_model=OutputModel,
    client=client,
    config=config,
)
```

### Control Logging

```python
from pydantic_llm_io import LoggingConfig

config = LLMCallConfig(
    logging=LoggingConfig(
        level="DEBUG",              # Show detailed logs
        include_raw_response=False, # Don't log raw API responses
        include_validation_errors=True,
    )
)
```

### Custom System Prompt

```python
config = LLMCallConfig(
    custom_system_prompt="You are an expert summarizer. Always respond with valid JSON."
)
```

## Async Usage

```python
from pydantic_llm_io import call_llm_validated_async
import asyncio

async def main():
    result = await call_llm_validated_async(
        prompt_model=SummaryRequest(...),
        response_model=SummaryResponse,
        client=client,
    )
    return result

# Run it
result = asyncio.run(main())
```

## Error Handling

```python
from pydantic_llm_io import (
    RetryExhaustedError,
    LLMCallError,
    LLMParseError,
    LLMValidationError,
)

try:
    result = call_llm_validated(...)
except RetryExhaustedError as e:
    print(f"Failed after {e.context['attempts']} attempts")
    print(f"Last error: {e.context['last_error']}")
except LLMCallError as e:
    print(f"API request failed: {e.message}")
except LLMValidationError as e:
    print(f"Response validation failed: {e.context['validation_errors']}")
except LLMParseError as e:
    print(f"JSON parsing failed: {e.context['parse_error']}")
```

## Multiple Providers

The library works with any provider via the `ChatClient` interface:

```python
# OpenAI (built-in)
from pydantic_llm_io import OpenAIChatClient
client = OpenAIChatClient(api_key="sk-...")

# Your custom provider
class MyCustomClient(ChatClient):
    def send_message(self, system: str, user: str, temperature: float = 0.7) -> str:
        # Your implementation
        pass

    async def send_message_async(self, system: str, user: str, temperature: float = 0.7) -> str:
        # Your async implementation
        pass

    def get_provider_name(self) -> str:
        return "my_custom"

client = MyCustomClient(...)

# Use the same API for all providers
result = call_llm_validated(
    prompt_model=input_model,
    response_model=OutputModel,
    client=client,  # Works with any ChatClient
)
```

## Common Patterns

### Extract Structured Data

```python
class DataExtractionRequest(BaseModel):
    text: str

class Entity(BaseModel):
    name: str
    type: str  # PERSON, PLACE, ORGANIZATION

class DataExtractionResponse(BaseModel):
    entities: list[Entity]

result = call_llm_validated(
    prompt_model=DataExtractionRequest(text="Article text"),
    response_model=DataExtractionResponse,
    client=client,
)

for entity in result.entities:
    print(f"{entity.name} ({entity.type})")
```

### Generate Code

```python
class CodeGenerationRequest(BaseModel):
    function_description: str
    language: str

class CodeGenerationResponse(BaseModel):
    code: str
    explanation: str

result = call_llm_validated(
    prompt_model=CodeGenerationRequest(
        function_description="Sort a list",
        language="Python"
    ),
    response_model=CodeGenerationResponse,
    client=client,
)

print(result.code)
```

### Batch Processing with Async

```python
import asyncio

async def process_many(items: list[str]):
    tasks = [
        call_llm_validated_async(
            prompt_model=SummaryRequest(article_text=item, max_words=50),
            response_model=SummaryResponse,
            client=client,
        )
        for item in items
    ]
    return await asyncio.gather(*tasks)

# Process 10 articles concurrently
results = asyncio.run(process_many(articles))
```

## Next Steps

- Check [examples/](examples/) for more complete examples
- Read [README.md](README.md) for full API documentation
- See [DELIVERABLES.md](DELIVERABLES.md) for architecture details
- Run tests: `pytest tests/`

## Support

All functions include:
- Complete type hints (mypy compatible)
- Comprehensive docstrings
- Example usage in code comments
- Rich error messages with context

Happy building! 🚀
