"""The QA-assistant agent: a tool-calling agent built with LangChain.

Uses ``langchain.agents.create_agent`` — the stable v1 equivalent of the
legacy ``create_react_agent`` — wired to the three QA tools in ``src/tools.py``.
Runs fully offline against :class:`DeterministicFakeChatModel`; swap in a
real chat model with the one-line change in :func:`get_model`.
"""

from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage

from src.fake_model import DeterministicFakeChatModel
from src.tools import TOOLS

SYSTEM_PROMPT = (
    "You are AtlasQA, a QA assistant. You have three tools: "
    "`calculator` for arithmetic, `search_bugs` for the bug tracker, and "
    "`summarize_text` for summarizing reports. Call the right tool for the "
    "user's request, then give a concise final answer based on the tool result."
)


def get_model():
    # --- ONE-LINE SWAP ---------------------------------------------------
    # Replace the line below with this single line to use a real model:
    # from langchain_openai import ChatOpenAI; return ChatOpenAI(model="gpt-4o-mini")
    # (requires: pip install langchain-openai, and OPENAI_API_KEY set)
    # ---------------------------------------------------------------------
    return DeterministicFakeChatModel()


def build_qa_agent(model=None):
    """Build the tool-calling QA agent (LangGraph-backed, via create_agent)."""
    return create_agent(model or get_model(), TOOLS, system_prompt=SYSTEM_PROMPT)


def ask(question: str, agent=None) -> dict:
    """Ask the agent a question; return the full result state."""
    agent = agent or build_qa_agent()
    return agent.invoke({"messages": [HumanMessage(content=question)]})


def tools_used(result: dict) -> list[str]:
    """Names of tools the agent called, in order."""
    names: list[str] = []
    for message in result["messages"]:
        if isinstance(message, AIMessage):
            names.extend(call["name"] for call in message.tool_calls)
    return names


def final_answer(result: dict) -> str:
    """The agent's final answer text."""
    last = result["messages"][-1]
    content = last.content
    return content if isinstance(content, str) else str(content)
