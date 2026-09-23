"""Deterministic fake chat model for fully offline agent testing.

This subclasses LangChain's own testing fake
(:class:`langchain_core.language_models.fake_chat_models.GenericFakeChatModel`)
and overrides ``_generate`` with keyword-based routing, so the agent's tool
calls are 100% deterministic with no API key and no network.

Two deliberate deviations from a stock fake:

1. ``bind_tools`` returns ``self``. Real chat models inject tool schemas into
   the request; a fake has nothing to inject, but LangChain's agent factory
   (``langchain.agents.create_agent``) calls ``model.bind_tools(tools)``
   unconditionally, and the stock fakes raise ``NotImplementedError`` there.
2. ``_generate`` inspects the conversation and emits ``AIMessage.tool_calls``
   (or a final answer after a ``ToolMessage``) instead of popping a canned
   script. That keeps routing assertions meaningful: the *agent* decides
   which tool to call, not a pre-written message list.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import PrivateAttr
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import ChatResult
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langchain_core.outputs import ChatGeneration

# Word-form operators the fake normalizes before extracting an expression.
_WORD_OPERATORS = {
    "divided by": "/",
    "multiplied by": "*",
    "times": "*",
    "plus": "+",
    "minus": "-",
}

_CALC_TRIGGER = re.compile(r"\d\s*[+\-*/%]")
_EXPRESSION = re.compile(r"\(?\d[\d\s.+\-*/%()]*")
_SENTENCE_COUNT = re.compile(r"in (\d+) sentences?")
_BUG_WORDS = ("bug", "defect", "issue", "ticket", "crash", "fail", "error")

_FINAL_TEMPLATES = {
    "calculator": "The answer is {result}.",
    "search_bugs": "Here's what I found in the bug tracker:\n{result}",
    "summarize_text": "Summary:\n{result}",
}


class DeterministicFakeChatModel(GenericFakeChatModel):
    """A fake chat model that routes deterministically to the QA tools."""

    _call_counter: int = PrivateAttr(default=0)

    def __init__(self, **kwargs: Any) -> None:
        # The parent requires a messages iterator; routing overrides _generate,
        # so an empty iterator is fine.
        kwargs.setdefault("messages", iter([]))
        super().__init__(**kwargs)

    # -- tool binding -----------------------------------------------------
    def bind_tools(self, tools: Any, **kwargs: Any) -> "DeterministicFakeChatModel":
        """Fakes have no provider schema to inject; return self unchanged."""
        return self

    # -- routing ----------------------------------------------------------
    def _next_call_id(self) -> str:
        self._call_counter += 1
        return f"fake-call-{self._call_counter}"

    def _tool_call_message(self, name: str, args: dict) -> AIMessage:
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": name,
                    "args": args,
                    "id": self._next_call_id(),
                    "type": "tool_call",
                }
            ],
        )

    @staticmethod
    def _normalize_operators(text: str) -> str:
        for word, symbol in _WORD_OPERATORS.items():
            text = text.replace(word, f" {symbol} ")
        return text

    def _route(self, question: str) -> AIMessage | None:
        """Return an AIMessage with a tool call, or None for a direct answer."""
        lowered = question.lower()
        normalized = self._normalize_operators(lowered)

        # 1. calculator: digits plus an arithmetic operator (symbol or word form)
        if re.search(r"\d", normalized) and (
            "calculat" in normalized or _CALC_TRIGGER.search(normalized)
        ):
            match = _EXPRESSION.search(normalized)
            expression = match.group(0).strip() if match else question
            return self._tool_call_message("calculator", {"expression": expression})

        # 2. summarizer: explicit "summar*" beats bug keywords
        if "summar" in lowered:
            text = question.split(":", 1)[1].strip() if ":" in question else question
            count = _SENTENCE_COUNT.search(lowered)
            return self._tool_call_message(
                "summarize_text",
                {"text": text, "max_sentences": int(count.group(1)) if count else 3},
            )

        # 3. bug search: defect-tracker vocabulary
        if any(word in lowered for word in _BUG_WORDS):
            return self._tool_call_message("search_bugs", {"query": question})

        return None

    # -- chat model interface ---------------------------------------------
    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: CallbackManagerForLLMRun | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        last = messages[-1]

        # After a tool runs, turn its output into the final answer.
        if isinstance(last, ToolMessage):
            result = last.content if isinstance(last.content, str) else str(last.content)
            template = _FINAL_TEMPLATES.get(last.name or "", "{result}")
            answer = template.format(result=result)
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=answer))])

        question = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
            "",
        )
        routed = self._route(question if isinstance(question, str) else str(question))
        if routed is not None:
            return ChatResult(generations=[ChatGeneration(message=routed)])

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(
                        content=(
                            "I can help with calculations, searching the bug "
                            "tracker, and summarizing text. What do you need?"
                        )
                    )
                )
            ]
        )
