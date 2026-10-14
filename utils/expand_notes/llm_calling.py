from typing import Any, Callable, Optional

from .llm_model import select_model

DEFAULT_MODEL = "openai"


def call_llm(
    prompt: str,
    model: str = DEFAULT_MODEL,
    tools: Optional[list[dict]] = None,
    handlers: Optional[dict[str, Callable[..., Any]]] = None,
    system: Optional[str] = None,
    max_turns: int = 5,
    **kwargs,
) -> str:
    adapter = select_model(model)
    handlers = handlers or {}

    messages: list = [{"role": "user", "content": prompt}]

    for _ in range(max_turns):
        response = adapter.run(messages, tools=tools, system=system, **kwargs)

        tool_calls = response.get("tool_calls") or []
        if not tool_calls:
            return response.get("content") or ""

        results = []
        for call in tool_calls:
            handler = handlers.get(call["name"])

            if handler is None:
                output = {"error": f"No handler registered for tool '{call['name']}'"}
            else:
                try:
                    output = handler(**call.get("arguments", {}))
                except Exception as exc:  
                    output = {"error": str(exc)}

            results.append({"id": call["id"], "name": call["name"], "content": output})

        messages = adapter.append_tool_results(messages, response["raw"], results)

    raise RuntimeError(f"Tool-calling exceeded max_turns ({max_turns}) without a final answer.")
