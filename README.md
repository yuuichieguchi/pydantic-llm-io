# pydantic-llm-io

**Type-safe, validated input/output handling for LLM calls.**

`pydantic-llm-io` is a Python library that provides type safety and validation for large language model (LLM) interactions. It combines Pydantic models for strict schema validation with automatic retry logic and detailed error handling.

## Features

- **Type-Safe I/O**: Define input and output schemas using Pydantic models
- **Automatic Validation**: JSON parsing and Pydantic schema validation with clear error messages
- **Smart Retries**: Exponential backoff retries with LLM self-correction prompts
- **Multi-Provider Support**: Clean abstraction for easy provider switching (OpenAI, Anthropic, custom)
- **Async Support**: Full async/await support for concurrent LLM calls
- **Excellent Errors**: Rich error context including raw responses and validation details
- **Flexible Logging**: Configurable logging with sensitive data controls

## Installation

```bash
# Basic installation (without LLM provider)
pip install pydantic-llm-io

# With OpenAI support
pip install pydantic-llm-io[openai]

# With development dependencies
pip install pydantic-llm-io[dev]
```

### Dependencies

- Python 3.10+
- pydantic >= 2.0
- openai >= 1.0 (optional, required only if using OpenAIChatClient)

## Quick Start

### 1. Define Your Models

```python
from pydantic import BaseModel, Field

class SummaryInput(BaseModel):
    """Schema for summarization input."""
    text: str = Field(..., description="Text to summarize")
    max_words: int = Field(100, description="Maximum summary length")

class SummaryOutput(BaseModel):
    """Schema for summarization output."""
    summary: str
    key_points: list[str]
    language: str
```

### 2. Call LLM with Validation

```python
from pydantic_llm_io import call_llm_validated, OpenAIChatClient

# Initialize client
client = OpenAIChatClient(api_key="sk-...")

# Make validated call
result = call_llm_validated(
    prompt_model=SummaryInput(text="Long article...", max_words=50),
    response_model=SummaryOutput,
    client=client,
)

# Result is fully typed and validated
print(result.summary)
print(result.key_points)
```

That's it! The library handles:

✅ Serializing your input model to JSON
✅ Constructing system and user prompts with schema injection
✅ Calling the LLM API
✅ Parsing JSON response
✅ Validating against your output model
✅ Retrying with corrections if validation fails

## Configuration

### Retry Behavior

```python
from pydantic_llm_io import LLMCallConfig, RetryConfig

config = LLMCallConfig(
    retry=RetryConfig(
        max_retries=3,                    # Retry up to 3 times
        initial_delay_seconds=1.0,        # First retry after 1 second
        backoff_multiplier=2.0,           # Double delay each time (1s, 2s, 4s)
    )
)

result = call_llm_validated(
    prompt_model=input_model,
    response_model=OutputModel,
    client=client,
    config=config,
)
```

### Logging Configuration

```python
from pydantic_llm_io import LoggingConfig

config = LLMCallConfig(
    logging=LoggingConfig(
        level="DEBUG",                    # DEBUG, INFO, WARNING, ERROR
        include_raw_response=True,        # Include full LLM response in logs
        include_validation_errors=True,   # Include validation error details
    )
)
```

### Custom System Prompt

```python
config = LLMCallConfig(
    custom_system_prompt="You are an expert JSON generator for summaries."
)
```

## Async Usage

```python
import asyncio
from pydantic_llm_io import call_llm_validated_async

async def main():
    result = await call_llm_validated_async(
        prompt_model=input_model,
        response_model=OutputModel,
        client=client,
    )
    return result

asyncio.run(main())
```

## Error Handling

The library provides detailed exceptions:

```python
from pydantic_llm_io import (
    LLMCallError,      # API request failed
    LLMParseError,     # JSON parsing failed
    LLMValidationError, # Pydantic validation failed
    RetryExhaustedError, # All retries failed
)

try:
    result = call_llm_validated(...)
except RetryExhaustedError as e:
    print(f"Failed after {e.context['attempts']} attempts")
    print(f"Last error: {e.context['last_error']}")
except LLMValidationError as e:
    print(f"Validation errors: {e.context['validation_errors']}")
```

## Testing

Use `FakeChatClient` for testing without API calls:

```python
import json
from pydantic_llm_io import FakeChatClient, call_llm_validated

# Create fake client with predefined response
response = json.dumps({
    "summary": "Test summary",
    "key_points": ["point1", "point2"],
    "language": "English"
})

client = FakeChatClient(response)

# Use in tests exactly like real client
result = call_llm_validated(
    prompt_model=input_model,
    response_model=OutputModel,
    client=client,
)

# Inspect calls made
assert client.call_count == 1
assert "schema" in client.last_system
```

## Architecture

### Provider Abstraction

The library uses an abstract `ChatClient` interface for provider independence:

```python
from pydantic_llm_io import ChatClient

class CustomClient(ChatClient):
    """Custom provider implementation."""

    def send_message(self, system: str, user: str, temperature: float = 0.7) -> str:
        # Your provider logic here
        pass

    async def send_message_async(self, system: str, user: str, temperature: float = 0.7) -> str:
        # Your async provider logic here
        pass

    def get_provider_name(self) -> str:
        return "custom"

# Use your custom client
client = CustomClient(api_key="...")
result = call_llm_validated(..., client=client)
```

Adding new providers requires only implementing the `ChatClient` interface. The rest of the library is provider-agnostic.

## How Retries Work

When validation fails, the library:

1. Catches the validation error (JSON parse or Pydantic schema)
2. Waits using exponential backoff
3. Sends a **correction prompt** to the LLM with error details
4. The LLM can see what went wrong and fix it
5. Retries validation
6. Repeats until success or max retries exhausted

This leverages the LLM's ability to self-correct, significantly improving success rates for structured outputs.

## Examples

See the `examples/` directory for:

- `basic_usage.py` - Simple summarization with FakeChatClient
- `with_openai.py` - Code review using OpenAI API
- `async_example.py` - Concurrent translations with async

## API Reference

### Main Functions

#### `call_llm_validated()`

```python
def call_llm_validated(
    prompt_model: PromptModelT,           # Input schema instance
    response_model: type[ResponseModelT],  # Output schema class
    client: ChatClient,                    # Provider client
    config: LLMCallConfig | None = None,   # Optional configuration
) -> ResponseModelT:
    """Call LLM with type-safe validation."""
```

#### `call_llm_validated_async()`

Async version of `call_llm_validated()`.

### Classes

- **`LLMCallConfig`**: Complete configuration (retry, logging, temperature, etc.)
- **`RetryConfig`**: Retry strategy configuration
- **`LoggingConfig`**: Logging detail level
- **`ChatClient`**: Abstract provider interface
- **`OpenAIChatClient`**: OpenAI implementation
- **`FakeChatClient`**: Testing double

### Exceptions

- **`LLMIOError`**: Base exception
- **`LLMCallError`**: API request failed
- **`LLMParseError`**: JSON parsing failed
- **`LLMValidationError`**: Pydantic validation failed
- **`RetryExhaustedError`**: All retries exhausted
- **`ConfigError`**: Configuration error

## Contributing

Contributions welcome! Areas for enhancement:

- Additional provider implementations (Anthropic, Cohere, local models)
- Streaming response support
- Token counting and cost estimation
- Structured caching of responses
- Additional validation strategies

## License

MIT

## Support

For issues, questions, or suggestions:

- Open an issue on [GitHub](https://github.com/anthropics/pydantic-llm-io)
- Check [documentation](https://github.com/anthropics/pydantic-llm-io#readme)
