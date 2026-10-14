import json
import os

from anthropic import Anthropic

DEFAULT_MODEL = "claude-3-5-sonnet-latest"


def _client(api_key: str | None = None) -> Anthropic:
    return Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))


def run(
    messages,
    tools=None,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    system: str | None = None,
    max_tokens: int = 1024,
    **kwargs,
) -> dict:
    params = {"model": model, "messages": messages, "max_tokens": max_tokens}

    if system:
        params["system"] = system
    if tools:
        params["tools"] = tools

    params.update(kwargs)

    resp = _client(api_key).messages.create(**params)

    tool_calls = []
    text_parts = []
    for block in resp.content:
        if block.type == "tool_use":
            tool_calls.append(
                {"id": block.id, "name": block.name, "arguments": block.input}
            )
        elif block.type == "text":
            text_parts.append(block.text)

    return {
        "content": "".join(text_parts) or None,
        "tool_calls": tool_calls,
        "raw": [b.model_dump() for b in resp.content],
    }


def append_tool_results(messages, raw, results) -> list:
    messages.append({"role": "assistant", "content": raw})

    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": r["id"],
                    "content": r["content"]
                    if isinstance(r["content"], str)
                    else json.dumps(r["content"]),
                }
                for r in results
            ],
        }
    )

    return messages
