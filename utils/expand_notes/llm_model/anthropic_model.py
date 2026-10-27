import os

from anthropic import Anthropic

DEFAULT_MODEL = "claude-3-5-sonnet-latest"
DEFAULT_MAX_TOKENS = 900


def _client(api_key: str | None = None) -> Anthropic:
    return Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))


def run(
    messages,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    system: str | None = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    **kwargs,
) -> dict:
    kwargs.pop("tools", None)

    params = {"model": model, "messages": messages, "max_tokens": max_tokens}

    if system:
        params["system"] = system

    params.update(kwargs)

    resp = _client(api_key).messages.create(**params)

    text = "".join(block.text for block in resp.content if block.type == "text")

    return {"content": text or None}
