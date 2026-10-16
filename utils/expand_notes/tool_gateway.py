from .tools.text_expand import expand_text
from .tools.text_to_notion import text_to_notion_blocks


def expand_note(text: str, model: str = "openai") -> list[dict]:
    expanded = expand_text(text, model=model)

    if not expanded or not expanded.strip():
        raise RuntimeError("Expand step returned empty text.")

    blocks = text_to_notion_blocks(expanded, model=model)

    if not blocks:
        raise RuntimeError("Notion conversion step returned no blocks.")

    return blocks


