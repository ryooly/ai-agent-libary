import os
import requests
from typing import Optional


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

    def fill_content(self, page_id: str, fills: list[dict]) -> dict:
        block = {"children": fills}
        return self._patch(f"/blocks/{page_id}/children", block) # added a expand text function here, so users insert a text then ai ll send it to the a function with llm and process it there 

    def _resolve_parent(self, parent_folder: Optional[str] = None) -> dict:
        if parent_folder:
            return {"type": "page_id", "page_id": parent_folder}
        return {"type": "workspace", "workspace": True}

    def _post(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        resp = requests.post(url, headers=self._headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def _patch(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base_url}{endpoint}"
        resp = requests.patch(url, headers=self._headers, json=payload)
        resp.raise_for_status()
        return resp.json()


_client: Optional[NotionRemote] = None


def _get_client() -> NotionRemote:
    global _client
    if _client is None:
        _client = NotionRemote()
    return _client


def create_folder(title: str, parent_folder: Optional[str] = None) -> dict:
    return _get_client().create_folder(title, parent_folder)


def create_file(title: str, parent_folder: Optional[str] = None) -> dict:
    return _get_client().create_file(title, parent_folder)


def add_text(page_id: str, fill: dict) -> dict:
    return _get_client().add_text(page_id, fill)


def edit_title(page_id: str, title: str) -> dict:
    return _get_client().edit_title(page_id, title)


def fill_content(page_id: str, fills: list[dict]) -> dict:
    return _get_client().fill_content(page_id, fills)
