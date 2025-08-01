import os
from typing import Generator, Union

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def generate_llm_response(
    input: list[dict],
    model: str = "gpt-4.1",
    temperature: float = 0,
    stream: bool = False,
) -> Union[str, Generator[str, None, None]]:
    """Generate LLM response with optional streaming support."""

    if stream:
        # Return a generator for streaming
        return _stream_llm_response(input, model, temperature)
    else:
        # Return complete response
        response = client.chat.completions.create(
            model=model,
            messages=input,
            temperature=temperature,
        )
        return response.choices[0].message.content


def _stream_llm_response(
    input: list[dict],
    model: str = "gpt-4.1",
    temperature: float = 0,
) -> Generator[str, None, None]:
    """Stream LLM response chunk by chunk."""

    stream = client.chat.completions.create(
        model=model,
        messages=input,
        temperature=temperature,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
