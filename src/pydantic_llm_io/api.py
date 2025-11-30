"""Main API for type-safe LLM calls."""

import logging
from typing import Any

from pydantic import BaseModel

from .clients.base import ChatClient
from .config import LLMCallConfig, LoggingConfig
from .exceptions import LLMCallError
from .logging import setup_logger
from .prompts import PromptBuilder
from .types import PromptModelT, ResponseModelT
from .validation import ValidationEngine


def call_llm_validated(
    prompt_model: PromptModelT,
    response_model: type[ResponseModelT],
    client: ChatClient,
    config: LLMCallConfig | None = None,
) -> ResponseModelT:
    """Call LLM with type-safe input/output validation.

    Args:
        prompt_model: Pydantic model containing user prompt
        response_model: Pydantic model for response validation
        client: Chat client instance (OpenAI, Fake, etc.)
        config: Optional LLMCallConfig for retries, logging, custom system

    Returns:
        Validated response model instance

    Raises:
        LLMCallError: If API request fails
        LLMParseError: If JSON parsing fails
        LLMValidationError: If Pydantic validation fails
        RetryExhaustedError: If all retries are exhausted
    """
    config = config or LLMCallConfig()
    logger = setup_logger("pydantic_llm_io.api", config.logging)

    # Build prompt
    prompt_builder = PromptBuilder(config.custom_system_prompt)
    schema = response_model.model_json_schema()
    system, user = prompt_builder.build(prompt_model, schema)

    logger.debug(f"System prompt:\n{system[:200]}...")
    logger.debug(f"User message:\n{user[:200]}...")

    # Get response from LLM
    try:
        response_text = client.send_message(
            system=system,
            user=user,
            temperature=config.temperature,
        )
        logger.debug(f"LLM response:\n{response_text[:200]}...")
    except LLMCallError as e:
        logger.error(f"LLM request failed: {e.message}", extra={"context": e.context})
        raise

    # Validate with retries
    engine = ValidationEngine(config.retry, config.logging, logger)
    try:
        result = engine.validate_with_retries(
            response_text=response_text,
            response_model=response_model,
            client=client,
            prompt_system=system,
            prompt_user=user,
        )
        logger.info(f"Successfully validated response to {response_model.__name__}")
        return result
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise


async def call_llm_validated_async(
    prompt_model: PromptModelT,
    response_model: type[ResponseModelT],
    client: ChatClient,
    config: LLMCallConfig | None = None,
) -> ResponseModelT:
    """Call LLM with type-safe input/output validation (async).

    Args:
        prompt_model: Pydantic model containing user prompt
        response_model: Pydantic model for response validation
        client: Chat client instance (OpenAI, Fake, etc.)
        config: Optional LLMCallConfig for retries, logging, custom system

    Returns:
        Validated response model instance

    Raises:
        LLMCallError: If API request fails
        LLMParseError: If JSON parsing fails
        LLMValidationError: If Pydantic validation fails
        RetryExhaustedError: If all retries are exhausted
    """
    config = config or LLMCallConfig()
    logger = setup_logger("pydantic_llm_io.api", config.logging)

    # Build prompt
    prompt_builder = PromptBuilder(config.custom_system_prompt)
    schema = response_model.model_json_schema()
    system, user = prompt_builder.build(prompt_model, schema)

    logger.debug(f"System prompt:\n{system[:200]}...")
    logger.debug(f"User message:\n{user[:200]}...")

    # Get response from LLM (async)
    try:
        response_text = await client.send_message_async(
            system=system,
            user=user,
            temperature=config.temperature,
        )
        logger.debug(f"LLM response:\n{response_text[:200]}...")
    except LLMCallError as e:
        logger.error(f"LLM request failed: {e.message}", extra={"context": e.context})
        raise

    # Validate with retries (async)
    engine = ValidationEngine(config.retry, config.logging, logger)
    try:
        result = await engine.validate_with_retries_async(
            response_text=response_text,
            response_model=response_model,
            client=client,
            prompt_system=system,
            prompt_user=user,
        )
        logger.info(f"Successfully validated response to {response_model.__name__}")
        return result
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        raise
