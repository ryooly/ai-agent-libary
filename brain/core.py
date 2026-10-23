import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from tools.notion_tools import (
    add_text,
    create_file,
    create_folder,
    edit_title,
    fill_content,
)

TOOLS = [create_folder, create_file, add_text, edit_title, fill_content]

SYSTEM_PROMPT = (
    "You are a personal assistant that manages the user's Notion workspace. "
    "Use the available tools to create folders and files, append text blocks, "
    "rename pages, and fill pages with expanded content. "
    "When a tool returns a new page id, remember it for follow-up actions in the same task. "
    "Answer briefly and confirm what was done."
)


def build_llm(model: str = "gpt-4o-mini", temperature: float = 0.2) -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass it explicitly.")
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key)


def build_agent(llm: ChatOpenAI | None = None):
    llm = llm or build_llm()
    return create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)


def run(user_input: str, llm: ChatOpenAI | None = None) -> str:
    agent = build_agent(llm) # tambahkan stroutParser
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_input}],
    })
    return result["messages"][-1].content


if __name__ == "__main__":
    import sys

    task = " ".join(sys.argv[1:]) or "Create a Notion folder called 'My Notes' and report its page id."
    print(run(task))
