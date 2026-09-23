"""LCEL chains for the QA assistant.

The triage chain is a classic LangChain Expression Language pipeline:
prompt -> model -> output parser. It runs offline against a canned
``GenericFakeChatModel``; pass any chat model to ``build_triage_chain`` to
run it for real.
"""

from __future__ import annotations

import itertools

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

TRIAGE_SYSTEM = (
    "You are a QA triage assistant. Given a bug report, reply with exactly "
    "one line in this format: SEVERITY=<critical|major|minor> COMPONENT=<name>."
)


def build_triage_chain(model=None):
    """Build the bug-triage LCEL chain: prompt | model | StrOutputParser."""
    prompt = ChatPromptTemplate.from_messages(
        [("system", TRIAGE_SYSTEM), ("human", "{report}")]
    )
    model = model or GenericFakeChatModel(
        messages=itertools.cycle(
            [
                "SEVERITY=major COMPONENT=checkout",
                "SEVERITY=critical COMPONENT=payments",
            ]
        )
    )
    return prompt | model | StrOutputParser()


def triage(report: str, chain=None) -> str:
    """Classify a bug report's severity and component."""
    chain = chain or build_triage_chain()
    return chain.invoke({"report": report})
