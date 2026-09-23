"""Tests for the tool-calling QA agent.

Every test runs fully offline against the deterministic fake model and
asserts both tool routing (which tool the agent called) and the final
answer content.
"""

import json

import pytest
from langchain_core.messages import AIMessage

from src.agent import ask, build_qa_agent, final_answer, tools_used
from src.run_eval import GOLDEN_PATH

agent = build_qa_agent()


def _golden_tasks():
    with open(GOLDEN_PATH, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


@pytest.mark.parametrize("task", _golden_tasks(), ids=lambda t: t["id"])
def test_golden_task_routes_to_expected_tool_and_answers(task):
    result = ask(task["task"], agent=agent)
    routed = tools_used(result)

    assert task["expected_tool"] in routed, (
        f"expected tool {task['expected_tool']!r}, agent called {routed}"
    )

    answer = final_answer(result)
    for expected in task["expected_contains"]:
        assert expected in answer, (
            f"expected {expected!r} in final answer, got: {answer!r}"
        )


def test_agent_calls_exactly_one_tool_per_golden_task():
    for task in _golden_tasks():
        result = ask(task["task"], agent=agent)
        assert len(tools_used(result)) == 1, f"{task['id']}: {tools_used(result)}"


def test_tool_calls_carry_well_formed_arguments():
    result = ask("Calculate 240 * 16 + 128", agent=agent)
    calls = [
        call
        for message in result["messages"]
        if isinstance(message, AIMessage)
        for call in message.tool_calls
    ]
    assert calls, "agent should have emitted a tool call"
    call = calls[0]
    assert call["name"] == "calculator"
    assert call["args"]["expression"].strip() == "240 * 16 + 128"
    assert call["id"].startswith("fake-call-")


def test_unrecognized_question_gets_graceful_answer_without_tools():
    result = ask("Hello, who are you?", agent=agent)
    assert tools_used(result) == []
    answer = final_answer(result)
    assert "calculator" in answer or "bug" in answer
