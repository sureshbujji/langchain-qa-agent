"""Golden-set evaluation for the QA agent.

Runs every task in ``data/golden_tasks.jsonl`` through the agent, checks that
it routed to the expected tool and that the final answer contains the expected
substrings, prints a summary table, and writes ``reports/eval_report.md``.

Fully offline: uses the deterministic fake model, no API key required.

Usage:
    python -m src.run_eval [--report reports/eval_report.md]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.agent import ask, build_qa_agent, final_answer, tools_used

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLDEN_PATH = REPO_ROOT / "data" / "golden_tasks.jsonl"
DEFAULT_REPORT = REPO_ROOT / "reports" / "eval_report.md"


def load_golden_tasks(path: Path = GOLDEN_PATH) -> list[dict]:
    tasks = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                tasks.append(json.loads(line))
    return tasks


def evaluate_task(agent, task: dict) -> dict:
    result = ask(task["task"], agent=agent)
    routed = tools_used(result)
    answer = final_answer(result)
    tool_ok = task["expected_tool"] in routed
    missing = [s for s in task["expected_contains"] if s not in answer]
    return {
        "id": task["id"],
        "task": task["task"],
        "expected_tool": task["expected_tool"],
        "routed_tools": routed,
        "tool_ok": tool_ok,
        "missing": missing,
        "passed": tool_ok and not missing,
        "answer": answer,
    }


def evaluate(agent=None, tasks: list[dict] | None = None) -> list[dict]:
    agent = agent or build_qa_agent()
    return [evaluate_task(agent, task) for task in (tasks or load_golden_tasks())]


def render_report(results: list[dict]) -> str:
    passed = sum(1 for r in results if r["passed"])
    lines = [
        "# QA Agent Eval Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} "
        f"| Model: DeterministicFakeChatModel (offline, no API key)",
        "",
        f"**{passed}/{len(results)} tasks passed**",
        "",
        "| Task | Expected tool | Routed tools | Answer check | Pass |",
        "| ---- | ------------- | ------------ | ------------ | ---- |",
    ]
    for r in results:
        answer_check = "ok" if not r["missing"] else f"missing: {', '.join(r['missing'])}"
        lines.append(
            f"| {r['id']} | `{r['expected_tool']}` | "
            f"{', '.join(f'`{t}`' for t in r['routed_tools']) or '—'} | "
            f"{answer_check} | {'✅' if r['passed'] else '❌'} |"
        )
    lines += ["", "## Final answers", ""]
    for r in results:
        lines += [f"### {r['id']}: {r['task']}", "", "```", r["answer"], "```", ""]
    return "\n".join(lines)


def main(report_path: Path = DEFAULT_REPORT) -> int:
    results = evaluate()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_report(results), encoding="utf-8")

    passed = sum(1 for r in results if r["passed"])
    print(f"\nEval: {passed}/{len(results)} passed -> {report_path}")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['id']}: routed={r['routed_tools']}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the QA agent golden-set eval.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    sys.exit(main(args.report))
