from typing import Optional

DEFAULT_MODEL = "openai"


def ask(
    prompt: str,
    model: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    **kwargs,
) -> str:
    messages = [{"role": "user", "content": prompt}]
    return chat(messages, model=model, system=system, **kwargs)


def chat(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    **kwargs,
) -> str:
    from . import select_model

    adapter = select_model(model)
    response = adapter.run(messages, system=system, **kwargs)
    return response.get("content") or ""
