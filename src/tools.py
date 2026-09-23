"""Tools for the QA assistant agent.

All three tools are fully offline and deterministic:

- ``calculator``: safe arithmetic evaluation (``ast``-based, no ``eval``).
- ``search_bugs``: keyword search over the local mock bug tracker
  (``data/bugs.json``).
- ``summarize_text``: extractive summarizer (first-N-sentences, stdlib only).
"""

from __future__ import annotations

import ast
import json
import operator
import re
from pathlib import Path

from langchain_core.tools import tool

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# ---------------------------------------------------------------------------
# calculator
# ---------------------------------------------------------------------------

_SAFE_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_SAFE_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(node: ast.AST) -> float:
    """Evaluate an AST node, allowing only numeric literals and safe operators."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_BINOPS:
        return _SAFE_BINOPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_UNARYOPS:
        return _SAFE_UNARYOPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"unsupported expression: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression like '240 * 16 + 128'.

    Supports +, -, *, /, %, ** and parentheses. Only numeric literals and
    safe operators are allowed; anything else returns an error string.
    """
    try:
        result = _safe_eval(ast.parse(expression.strip(), mode="eval").body)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as exc:  # noqa: BLE001 - surface as a tool result, not a crash
        return f"Error: {exc}"
    return str(result)


# ---------------------------------------------------------------------------
# search_bugs
# ---------------------------------------------------------------------------


def _load_bugs() -> list[dict]:
    with open(DATA_DIR / "bugs.json", encoding="utf-8") as fh:
        return json.load(fh)


_STOPWORDS = frozenset(
    "the a an and or of to in on for with are is was were be been there here "
    "any all some me my you your show find search about related open bugs bug "
    "defects defect issues issue tickets ticket".split()
)


def _score_bug(bug: dict, tokens: list[str]) -> int:
    haystack = " ".join(
        [
            bug["id"],
            bug["title"],
            bug["description"],
            bug["component"],
            bug["severity"],
            bug["status"],
            " ".join(bug["tags"]),
        ]
    ).lower()
    return sum(haystack.count(token) for token in tokens)


@tool
def search_bugs(query: str, max_results: int = 5) -> str:
    """Search the mock bug tracker for bugs matching a natural-language query.

    Returns up to ``max_results`` matches as 'ID | title (severity, status)'
    lines, ranked by keyword overlap.
    """
    bugs = _load_bugs()
    tokens = [
        token
        for token in re.findall(r"[a-z0-9]+", query.lower())
        if token not in _STOPWORDS
    ]
    if not tokens:
        return "No matching bugs found."
    ranked = sorted(
        ((bug, _score_bug(bug, tokens)) for bug in bugs),
        key=lambda pair: pair[1],
        reverse=True,
    )
    hits = [bug for bug, score in ranked if score > 0][:max_results]
    if not hits:
        return "No matching bugs found."
    return "\n".join(
        f"{bug['id']} | {bug['title']} ({bug['severity']}, {bug['status']})"
        for bug in hits
    )


# ---------------------------------------------------------------------------
# summarize_text
# ---------------------------------------------------------------------------

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@tool
def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Summarize text extractively by returning the first ``max_sentences``."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    return " ".join(sentences[:max_sentences])


TOOLS = [calculator, search_bugs, summarize_text]
