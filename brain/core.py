import logging
import os

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

from tools.notion_tools import (
    add_text,
    create_file,
    create_folder,
    edit_title,
    fill_content,
)

logger = logging.getLogger("brain")

TOOLS = [create_folder, create_file, add_text, edit_title, fill_content]

SYSTEM_PROMPT = (
    "You are a personal assistant that manages the user's Notion workspace. "
    "Use the available tools to create folders and files, append text blocks, "
    "rename pages, and fill pages with expanded content. "
    "When a tool returns a new page id, remember it for follow-up actions in the same task. "
    "Answer briefly and confirm what was done."
)


GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def build_llm(model: str = "qwen/qwen3.8-27b", temperature: float = 0.2) -> ChatOpenAI:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("Groq API key is required. Set GROQ_API_KEY env var or pass it explicitly.")
    logger.info("Building LLM %s (temperature=%s) via %s", model, temperature, GROQ_BASE_URL)
    return ChatOpenAI(model=model, temperature=temperature, api_key=api_key, base_url=GROQ_BASE_URL)


def build_agent(llm: ChatOpenAI | None = None):
    llm = llm or build_llm()
    agent = create_agent(model=llm, tools=TOOLS, system_prompt=SYSTEM_PROMPT)
    logger.info("Agent ready with tools: %s", ", ".join(t.name for t in TOOLS))
    return agent


def run(user_input: str, llm: ChatOpenAI | None = None) -> str:
    agent = build_agent(llm)
    logger.info("Task received: %s", user_input)
    result = agent.invoke({
        "messages": [{"role": "user", "content": user_input}],
    })
    for message in result["messages"]:
        for call in getattr(message, "tool_calls", []) or []:
            logger.info("Agent called tool: %s", call["name"])
    answer = result["messages"][-1].content
    logger.info("Task finished")
    return answer


def setup_console_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


if __name__ == "__main__":
    import sys

    setup_console_logging()
    subject = " ".join(sys.argv[1:]) or "My Notes"
    task = (
        f"Create a new Notion folder called '{subject}', then create a page inside it "
        f"with title '{subject}' and fill it with expanded content about {subject}."
    )
    print(run(task))
