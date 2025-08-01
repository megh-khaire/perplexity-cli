import os
from typing import Generator, Union

from dotenv import load_dotenv
from openai import OpenAI

from src.tools import ToolExecutor

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Global tool executor
tool_executor = ToolExecutor()


def generate_llm_response(
    input: list[dict],
    model: str = "gpt-4.1",
    temperature: float = 0,
    stream: bool = False,
    tools: list = None,
) -> Union[str, Generator[str, None, None], dict]:
    """Generate LLM response with optional streaming and tool calling support."""

    if stream and tools:
        # Tool calls don't work well with streaming, so we'll handle this differently
        return _stream_llm_response_with_tools(input, model, temperature, tools)
    elif stream:
        # Return a generator for streaming
        return _stream_llm_response(input, model, temperature)
    else:
        # Return complete response
        kwargs = {
            "model": model,
            "messages": input,
            "temperature": temperature,
        }

        if tools:
            kwargs["tools"] = tools

        response = client.chat.completions.create(**kwargs)

        # Check if there are tool calls
        if response.choices[0].message.tool_calls:
            return {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls,
            }

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


def _stream_llm_response_with_tools(
    input: list[dict],
    model: str = "gpt-4.1",
    temperature: float = 0,
    tools: list = None,
) -> Generator[str, None, None]:
    """Stream LLM response with tool calling support."""

    # First, make a non-streaming call to check for tool calls
    response = client.chat.completions.create(
        model=model,
        messages=input,
        temperature=temperature,
        tools=tools,
    )

    # If there are tool calls, process them
    if response.choices[0].message.tool_calls:
        # Yield the tool call indicator
        yield "Searching the internet...\n\n"

        # Execute tool calls
        tool_results = tool_executor.execute_tool_calls(
            response.choices[0].message.tool_calls
        )

        # Add tool results to conversation
        messages_with_tools = input.copy()

        # Add the assistant's message with tool calls
        messages_with_tools.append(
            {
                "role": "assistant",
                "content": response.choices[0].message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in response.choices[0].message.tool_calls
                ],
            }
        )

        # Add tool results
        for tool_call in response.choices[0].message.tool_calls:
            messages_with_tools.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_results[tool_call.id],
                }
            )

        # Get final response from LLM with tool results
        final_stream = client.chat.completions.create(
            model=model,
            messages=messages_with_tools,
            temperature=temperature,
            stream=True,
        )

        for chunk in final_stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    else:
        # No tool calls, stream normally
        stream = client.chat.completions.create(
            model=model,
            messages=input,
            temperature=temperature,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
