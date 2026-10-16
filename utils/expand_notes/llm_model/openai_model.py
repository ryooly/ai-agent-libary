import os

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-mini"


def _client(api_key: str | None = None) -> OpenAI:
    return OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))


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


# Pikirkn untuk menjadikan smeaunya satu aja
