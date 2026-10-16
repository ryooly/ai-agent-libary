from ..llm_calling import call_llm

EXPAND_SENTENCE_PROMPT = """You are a professional writing assistant.

Expand the SHORT TEXT below into well-developed, polished content.

RULES:
1. Keep the original meaning and intent — never change the message.
2. Add relevant detail, context, and examples where natural.
3. Improve flow and readability with clear sentence structure.
4. Match the tone of the original text.
5. Return ONLY the expanded text — no explanations, no markdown fences.

SHORT TEXT TO EXPAND:
\"\"\"{text}\"\"\"
"""


def build_expand_prompt(text: str) -> str:
    return EXPAND_SENTENCE_PROMPT.replace("{text}", text)


def expand_text(text: str, model: str = "openai", **llm_kwargs) -> str:
    prompt = build_expand_prompt(text)
    return call_llm(prompt, model=model, **llm_kwargs)
