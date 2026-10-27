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

_NOTION_CODE_LANGUAGES = {
    "abap", "arduino", "bash", "basic", "c", "clojure", "coffeescript",
    "c++", "c#", "css", "dart", "diff", "docker", "elixir", "elm", "erlang",
    "flow", "fortran", "f#", "gherkin", "glsl", "go", "graphql", "groovy",
    "haskell", "html", "java", "javascript", "json", "julia", "kotlin",
    "latex", "less", "lisp", "livescript", "lua", "makefile", "markdown",
    "markup", "matlab", "mermaid", "nix", "objective-c", "ocaml", "pascal",
    "perl", "php", "plain text", "powershell", "prolog", "protobuf", "python",
    "r", "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell",
    "sql", "swift", "typescript", "vb.net", "verilog", "vhdl", "visual basic",
    "webassembly", "xml", "yaml", "java/c/c++/c#",
}

_DEFAULT_CODE_LANGUAGE = "plain text"


def _safe_code_language(value) -> str:
    if isinstance(value, str):
        candidate = value.strip().lower()
        if candidate in _NOTION_CODE_LANGUAGES:
            return candidate
    return _DEFAULT_CODE_LANGUAGE


def _extract_json(raw: str) -> str:
    cleaned = raw.strip()

    fence = re.search(r"```(?:json)?\s*(.+?)\s*```", cleaned, re.DOTALL)
    if fence:
        cleaned = fence.group(1).strip()

    candidates = []
    for open_ch, close_ch in (("{", "}"), ("[", "]")):
        start = cleaned.find(open_ch)
        end = cleaned.rfind(close_ch)
        if start != -1 and end != -1 and end > start:
            candidates.append((start, cleaned[start : end + 1]))

    if candidates:
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

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

    if block_type == "code":
        new_body["language"] = _safe_code_language(body.get("language"))

    return {"object": "block", "type": block_type, block_type: new_body}


def text_to_notion_blocks(
    plain_text: str,
    model: str = "openai",
    **llm_kwargs,
) -> list[dict]:
    prompt = build_convert_prompt(plain_text)

    try:
        raw = ask(prompt, model=model, response_format={"type": "json_object"}, **llm_kwargs)
    except Exception:
        raw = ask(prompt, model=model, **llm_kwargs)

    data = json.loads(_extract_json(raw))

    if isinstance(data, dict):
        data = data.get("blocks", [])

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
