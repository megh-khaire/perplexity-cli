from typing import Dict, Generator, List, Union

from dotenv import load_dotenv

from .llm import generate_llm_response
from .prompt import load_prompt

load_dotenv()


def generate_conversation_response(
    messages: List[Dict[str, str]], stream: bool = False
) -> Union[str, Generator[str, None, None]]:
    """Generate a response with full conversation context."""
    system_prompt = load_prompt("generate_conversation_response")["system"]
    conversation = [{"role": "system", "content": system_prompt}]
    conversation.extend(messages)

    response = generate_llm_response(
        input=conversation,
        stream=stream,
    )
    return response
