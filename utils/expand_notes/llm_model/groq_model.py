import os

from openai import OpenAI

DEFAULT_MODEL = "llama-3.3-70b-versatile"

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

DEFAULT_MAX_TOKENS = 900


def _client(api_key: str | None = None) -> OpenAI:
    return OpenAI(
        api_key=api_key or os.getenv("GROQ_API_KEY"),
        base_url=GROQ_BASE_URL,
    )


def run(
    messages,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    system: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    **kwargs,
) -> dict:
    if system:
        messages = [{"role": "system", "content": system}, *messages]

    kwargs.pop("tools", None)

    params = {"model": model, "messages": messages, "max_tokens": max_tokens}
    params.update(kwargs)

    resp = _client(api_key).chat.completions.create(**params)

    return {"content": resp.choices[0].message.content}
