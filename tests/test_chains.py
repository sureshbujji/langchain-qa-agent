"""Tests for the LCEL triage chain."""

from src.chains import build_triage_chain, triage


def test_triage_chain_returns_severity_and_component():
    output = triage("Checkout button does nothing on Safari")
    assert "SEVERITY=" in output
    assert "COMPONENT=" in output


def test_triage_chain_is_reusable():
    chain = build_triage_chain()
    first = chain.invoke({"report": "Login times out"})
    second = chain.invoke({"report": "Payment charged twice"})
    assert "SEVERITY=" in first and "SEVERITY=" in second


def test_triage_chain_is_lcel():
    chain = build_triage_chain()
    # prompt | model | parser: a RunnableSequence
    assert hasattr(chain, "invoke") and hasattr(chain, "batch")
    assert type(chain).__name__ == "RunnableSequence"
