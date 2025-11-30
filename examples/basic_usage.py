"""Basic usage example with FakeChatClient (no API calls)."""

import json

from pydantic import BaseModel, Field

from pydantic_llm_io import (
    FakeChatClient,
    LLMCallConfig,
    call_llm_validated,
)


class ArticleInput(BaseModel):
    """Input model for article summarization."""

    article_text: str = Field(..., description="The full article text to summarize")
    max_summary_length: int = Field(100, description="Maximum length for summary in words")


class ArticleOutput(BaseModel):
    """Output model for article summary."""

    title: str = Field(..., description="A catchy title for the article")
    summary: str = Field(..., description="Concise summary of the article")
    key_topics: list[str] = Field(..., description="List of main topics covered")
    sentiment: str = Field(..., description="Overall sentiment: positive, negative, or neutral")


def main() -> None:
    """Run basic example."""
    # Create a fake client that returns a predefined response
    # (In real usage, you would use OpenAIChatClient instead)
    fake_response = json.dumps({
        "title": "Amazing Discovery in AI Research",
        "summary": "Scientists have made a breakthrough in AI that could revolutionize the field.",
        "key_topics": ["artificial intelligence", "machine learning", "breakthrough"],
        "sentiment": "positive",
    })

    client = FakeChatClient(fake_response)

    # Create input
    input_model = ArticleInput(
        article_text="Scientists announce a major breakthrough in AI research...",
        max_summary_length=100,
    )

    # Call LLM with validation
    result = call_llm_validated(
        prompt_model=input_model,
        response_model=ArticleOutput,
        client=client,
        config=LLMCallConfig(),
    )

    # Use the validated result
    print(f"Title: {result.title}")
    print(f"Summary: {result.summary}")
    print(f"Topics: {', '.join(result.key_topics)}")
    print(f"Sentiment: {result.sentiment}")


if __name__ == "__main__":
    main()
