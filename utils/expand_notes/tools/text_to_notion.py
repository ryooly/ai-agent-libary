import json
import re
from typing import Optional

from ..llm_model import ask
from .convert_prompt import build_convert_prompt

_ALLOWED_TYPES = {
    "paragraph",
    "heading_1",
    "heading_2",
    "heading_3",
    "bulleted_list_item",
    "numbered_list_item",
    "to_do",
    "quote",
    "callout",
    "code",
    "divider",
}


def _extract_json(raw: str) -> str:
    cleaned = raw.strip()

    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")
    if start != -1 and end != -1:
        return cleaned[start : end + 1]

    return cleaned


def _normalize_block(block: dict) -> Optional[dict]:
    block_type = block.get("type")

    if block_type not in _ALLOWED_TYPES:
        return None

    if block_type == "divider":
        return {"object": "block", "type": "divider", "divider": {}}

    body = block.get(block_type, {})
    rich_text = body.get("rich_text", [])

    normalized_rt = []
    for item in rich_text:
        text = item.get("text", {}).get("content", "")
        entry = {
            "type": "text",
            "text": {"content": text},
            "annotations": item.get("annotations", {}),
        }
        normalized_rt.append(entry)

    new_body = {**body, "rich_text": normalized_rt}
    return {"object": "block", "type": block_type, block_type: new_body}


def text_to_notion_blocks(
    plain_text: str,
    model: str = "openai",
    **llm_kwargs,
) -> list[dict]:
    prompt = build_convert_prompt(plain_text)
    raw = ask(prompt, model=model, **llm_kwargs)

    data = json.loads(_extract_json(raw))

    blocks = []
    for block in data:
        normalized = _normalize_block(block)
        if normalized is not None:
            blocks.append(normalized)

    return blocks


def text_to_notion_page(
    plain_text: str,
    model: str = "openai",
    **llm_kwargs,
) -> dict:
    from tools.notion_tools import fill_content

    blocks = text_to_notion_blocks(plain_text, model=model, **llm_kwargs)
    return blocks
