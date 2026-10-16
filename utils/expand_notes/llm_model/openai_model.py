import json
import os

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-mini"


def _client(api_key: str | None = None) -> OpenAI:
    return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))


def run(
    messages,
    tools=None,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    system: str | None = None,
    **kwargs,
) -> dict:
    if system:
        messages = [{"role": "system", "content": system}, *messages]

    params = {"model": model, "messages": messages}

    if tools:
        params["tools"] = tools
        params["tool_choice"] = "auto"

    params.update(kwargs)

    resp = _client(api_key).chat.completions.create(**params)
    msg = resp.choices[0].message

    tool_calls = []
    for tc in msg.tool_calls or []:
        tool_calls.append(
            {
                "id": tc.id,
                "name": tc.function.name,
                "arguments": json.loads(tc.function.arguments or "{}"),
            }
        )

    return {"content": msg.content, "tool_calls": tool_calls, "raw": msg}


def append_tool_results(messages, raw, results) -> list:
    messages.append(raw)

    for r in results:
        content = r["content"]
        if not isinstance(content, str):
            content = json.dumps(content)
        messages.append(
            {"role": "tool", "tool_call_id": r["id"], "content": content}
        )

    return messages


# Pikirkn untuk menjadikan smeaunya satu aja 