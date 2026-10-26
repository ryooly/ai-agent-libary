import os

from openai import OpenAI

DEFAULT_MODEL = "llama-3.3-70b-versatile"

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


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
    **kwargs,
) -> dict:
    if system:
        messages = [{"role": "system", "content": system}, *messages]

    kwargs.pop("tools", None)

    params = {"model": model, "messages": messages}
    params.update(kwargs)

    resp = _client(api_key).chat.completions.create(**params)

    return {"content": resp.choices[0].message.content}
