"""Shared fixtures: repo root on sys.path and a hermetic offline environment."""

import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(autouse=True)
def _offline_env(monkeypatch):
    """Scrub keys/tracing so the suite is hermetic even on a dev machine."""
    for var in (
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "LANGCHAIN_TRACING_V2",
        "LANGCHAIN_API_KEY",
        "LANGSMITH_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)
    yield
    # Prove no key leaked back in during the test.
    assert "OPENAI_API_KEY" not in os.environ
