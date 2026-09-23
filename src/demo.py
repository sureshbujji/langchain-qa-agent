"""Mock-mode smoke test: exercises the agent and the LCEL chain end to end.

One question per tool plus one triage-chain call, all offline with the
deterministic fake model. Exits 0 on success, non-zero on any failure.
Used by CI after pytest.

Usage:
    python -m src.demo
"""

from __future__ import annotations

import sys

from src.agent import ask, final_answer, tools_used
from src.chains import triage

SMOKE_CASES = [
    ("Calculate 12 * 12 + 6", "calculator", "150"),
    ("Find bugs related to login timeout", "search_bugs", "QA-1042"),
    (
        "Summarize this note: Alpha passed. Beta failed. Gamma was skipped.",
        "summarize_text",
        "Alpha passed",
    ),
]


def main() -> int:
    failures = 0

    for question, expected_tool, expected_text in SMOKE_CASES:
        result = ask(question)
        routed = tools_used(result)
        answer = final_answer(result)
        ok = expected_tool in routed and expected_text in answer
        print(f"[{'OK' if ok else 'FAIL'}] {question!r}")
        print(f"       routed={routed}")
        print(f"       answer={answer[:100]!r}")
        failures += 0 if ok else 1

    triage_out = triage("Checkout button does nothing on Safari")
    ok = "SEVERITY=" in triage_out and "COMPONENT=" in triage_out
    print(f"[{'OK' if ok else 'FAIL'}] triage chain -> {triage_out!r}")
    failures += 0 if ok else 1

    print(f"\nSmoke test: {'passed' if failures == 0 else f'{failures} FAILURES'}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
