"""Example using OpenAI API."""

import os

from pydantic import BaseModel, Field

from pydantic_llm_io import (
    LLMCallConfig,
    LoggingConfig,
    OpenAIChatClient,
    RetryConfig,
    call_llm_validated,
)


class CodeReviewInput(BaseModel):
    """Input for code review."""

    code: str = Field(..., description="Python code to review")
    focus_areas: list[str] = Field(
        default=["readability", "performance", "security"],
        description="Areas to focus on"
    )


class CodeReviewOutput(BaseModel):
    """Output for code review."""

    issues: list[str] = Field(..., description="Found issues")
    suggestions: list[str] = Field(..., description="Improvement suggestions")
    overall_grade: str = Field(..., description="Grade A-F")


def main() -> None:
    """Run code review example."""
    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAIChatClient(api_key=api_key, model="gpt-4o")

    # Create input
    input_model = CodeReviewInput(
        code="""
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price'] * item['quantity']
    return total
""",
        focus_areas=["readability", "performance"],
    )

    # Configure with retries and logging
    config = LLMCallConfig(
        retry=RetryConfig(max_retries=3, initial_delay_seconds=1.0),
        logging=LoggingConfig(level="INFO", include_raw_response=False),
        temperature=0.7,
    )

    # Call LLM with validation
    result = call_llm_validated(
        prompt_model=input_model,
        response_model=CodeReviewOutput,
        client=client,
        config=config,
    )

    # Display results
    print("=" * 50)
    print("CODE REVIEW RESULTS")
    print("=" * 50)
    print(f"\nOverall Grade: {result.overall_grade}")
    print("\nIssues Found:")
    for issue in result.issues:
        print(f"  - {issue}")
    print("\nSuggestions:")
    for suggestion in result.suggestions:
        print(f"  - {suggestion}")


if __name__ == "__main__":
    main()
