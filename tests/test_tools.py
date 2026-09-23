"""Unit tests for the three QA tools."""

import pytest

from src.tools import calculator, search_bugs, summarize_text


class TestCalculator:
    @pytest.mark.parametrize(
        "expression, expected",
        [
            ("2+3*4", "14"),
            ("240 * 16 + 128", "3968"),
            ("(100 - 37) * 2", "126"),
            ("10 / 4", "2.5"),
            ("2 ** 10", "1024"),
            ("17 % 5", "2"),
            ("-3 + 8", "5"),
        ],
    )
    def test_arithmetic(self, expression, expected):
        assert calculator.invoke({"expression": expression}) == expected

    def test_division_by_zero_is_an_error_string(self):
        result = calculator.invoke({"expression": "1 / 0"})
        assert result.startswith("Error:")

    def test_malicious_input_is_rejected_not_executed(self):
        result = calculator.invoke({"expression": "__import__('os').system('x')"})
        assert result.startswith("Error:")

    def test_name_access_is_rejected(self):
        result = calculator.invoke({"expression": "open('/etc/passwd').read()"})
        assert result.startswith("Error:")


class TestSearchBugs:
    def test_finds_login_timeout_bug(self):
        result = search_bugs.invoke({"query": "Find bugs related to login timeout"})
        assert "QA-1042" in result
        assert "Login times out on slow networks" in result

    def test_finds_payments_bug(self):
        result = search_bugs.invoke(
            {"query": "Search open critical defects in the payments flow"}
        )
        assert "QA-3301" in result

    def test_no_match_message(self):
        result = search_bugs.invoke({"query": "purple elephant refrigerator"})
        assert result == "No matching bugs found."

    def test_result_format(self):
        result = search_bugs.invoke({"query": "checkout"})
        first = result.splitlines()[0]
        assert first.startswith("QA-")
        assert "(" in first and ")" in first


class TestSummarizeText:
    TEXT = (
        "Alpha passed. Beta failed. Gamma was skipped. Delta is pending. "
        "Epsilon passed."
    )

    def test_default_is_three_sentences(self):
        result = summarize_text.invoke({"text": self.TEXT})
        assert result == "Alpha passed. Beta failed. Gamma was skipped."

    def test_max_sentences_is_respected(self):
        result = summarize_text.invoke({"text": self.TEXT, "max_sentences": 2})
        assert result == "Alpha passed. Beta failed."

    def test_short_text_returned_whole(self):
        result = summarize_text.invoke({"text": "Only one sentence."})
        assert result == "Only one sentence."
