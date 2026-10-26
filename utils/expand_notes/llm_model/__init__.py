import importlib

_MODEL_REGISTRY = {
    "openai": "openai_model",
    "gpt": "openai_model",
    "anthropic": "anthropic_model",
    "claude": "anthropic_model",
    "groq": "groq_model",
    "llama": "groq_model",
}


def list_models() -> list[str]:
    return sorted(_MODEL_REGISTRY.keys())


def select_model(model_name: str):
    key = (model_name or "").strip().lower()

    module_name = _MODEL_REGISTRY.get(key)
    if module_name is None:
        module_name = f"{key}_model"

    try:
        return importlib.import_module(f".{module_name}", __name__)
    except ModuleNotFoundError as exc:
        available = ", ".join(sorted(set(_MODEL_REGISTRY)))
        raise ValueError(
            f"Unknown model '{model_name}'. Available models: {available}"
        ) from exc


from .center import ask, chat

__all__ = ["select_model", "list_models", "ask", "chat"]

# Pikirkan gimana biar kita gak pelrlu nambah list mmodel setiap menambahkn model baru 