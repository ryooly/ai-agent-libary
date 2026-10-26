import logging
import os
import requests
from typing import Optional

from langchain_core.tools import tool


logger = logging.getLogger("brain.notion")


class NotionRemote:

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY", "")
        self.base_url = "https://api.notion.com/v1"
        self.version = "2022-06-28"

        if not self.api_key:
            raise ValueError("Notion API key is required. Set NOTION_API_KEY env var or pass api_key.")

        self._headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": self.version,
            "Content-Type": "application/json",
        }

    def create_folder(self, title: str, parent_folder: Optional[str] = None) -> dict:
        parent = self._resolve_parent(parent_folder)

        payload = {
            "parent": parent,
            "object": "page",
            "icon": {"emoji": "📁"},
            "properties": {
                "title": {"title": [{"text": {"content": title}}]},
            },
        }

        return self._post("/pages", payload)

    def create_file(self, title: str, parent_folder: Optional[str] = None) -> dict:
        parent = self._resolve_parent(parent_folder)

        payload = {
            "parent": parent,
            "object": "page",
            "properties": {
                "title": {"title": [{"text": {"content": title}}]},
            },
        }

        return self._post("/pages", payload)

    def add_text(self, page_id: str, fill: dict) -> dict:
        block = {"children": [fill]}
        return self._patch(f"/blocks/{page_id}/children", block) 

    def edit_title(self, page_id: str, title: str) -> dict:
        payload = {
            "properties": {
                "title": {"title": [{"text": {"content": title}}]},
            },
        }
        return self._patch(f"/pages/{page_id}", payload)

    def fill_content(self, page_id: str, text: str, model: str = "openai") -> dict:
        import sys
        from pathlib import Path

        project_root = str(Path(__file__).resolve().parent.parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)

        from utils.expand_notes.tool_gateway import expand_note

        blocks = expand_note(text, model=model)
        block = {"children": blocks}
        return self._patch(f"/blocks/{page_id}/children", block) 

    def _resolve_parent(self, parent_folder: Optional[str] = None) -> dict:
        if parent_folder:
            return {"type": "page_id", "page_id": parent_folder}
        return {"type": "workspace", "workspace": True}

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        logger.info("POST %s", endpoint)
        resp = requests.post(url, headers=self._headers, json=payload)
        if resp.status_code >= 400:
            logger.error("POST %s failed (%s): %s", endpoint, resp.status_code, resp.text[:300])
        resp.raise_for_status()
        return resp.json()

    def _patch(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        logger.info("PATCH %s", endpoint)
        resp = requests.patch(url, headers=self._headers, json=payload)
        if resp.status_code >= 400:
            logger.error("PATCH %s failed (%s): %s", endpoint, resp.status_code, resp.text[:300])
        resp.raise_for_status()
        return resp.json()


_client: Optional[NotionRemote] = None


def _get_client() -> NotionRemote:
    global _client
    if _client is None:
        _client = NotionRemote()
    return _client


@tool
def create_folder(title: str, parent_folder: Optional[str] = None) -> dict:
    """Create a new folder page in Notion.

    Args:
        title: The name of the folder to create.
        parent_folder: Optional id of a parent page/folder. Omit to create at the workspace root.

    Returns the created Notion folder page as a dictionary, including its new page id.
    """
    logger.info("create_folder title=%r parent=%s", title, parent_folder or "workspace root")
    result = _get_client().create_folder(title, parent_folder)
    logger.info("Folder created: page_id=%s", result.get("id"))
    return result


@tool
def create_file(title: str, parent_folder: Optional[str] = None) -> dict:
    """Create a new blank file page in Notion.

    Args:
        title: The name of the file/page to create.
        parent_folder: Optional id of a parent page/folder. Omit to create at the workspace root.

    Returns the created Notion page as a dictionary, including its new page id.
    """
    logger.info("create_file title=%r parent=%s", title, parent_folder or "workspace root")
    result = _get_client().create_file(title, parent_folder)
    logger.info("File created: page_id=%s", result.get("id"))
    return result


@tool
def add_text(page_id: str, fill: dict) -> dict:
    """Append a single raw block to an existing Notion page.

    Args:
        page_id: The id of the target Notion page or block.
        fill: A Notion block dictionary (e.g. a paragraph block) to append as a child.

    Returns the Notion API response as a dictionary.
    """
    logger.info("add_text page_id=%s block_type=%s", page_id, fill.get("type"))
    return _get_client().add_text(page_id, fill)


@tool
def edit_title(page_id: str, title: str) -> dict:
    """Rename the title of an existing Notion page.

    Args:
        page_id: The id of the Notion page to rename.
        title: The new title text.

    Returns the Notion API response as a dictionary.
    """
    logger.info("edit_title page_id=%s new_title=%r", page_id, title)
    return _get_client().edit_title(page_id, title)


@tool
def fill_content(page_id: str, text: str, model: str = "openai") -> dict:
    """Expand raw text into rich Notion blocks and append them to a page.

    Args:
        page_id: The id of the target Notion page.
        text: The raw short text to expand into structured content.
        model: The LLM provider used for expansion, e.g. "openai" or "anthropic".

    Returns the Notion API response as a dictionary.
    """
    logger.info("fill_content page_id=%s model=%s text=%r", page_id, model, text[:80])
    result = _get_client().fill_content(page_id, text, model)
    logger.info("fill_content done: %d block(s) appended", len(result.get("results", [])))
    return result
