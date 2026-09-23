"""Tests for the golden-set eval runner."""

from src.run_eval import evaluate, load_golden_tasks, render_report


def test_golden_file_has_ten_tasks():
    tasks = load_golden_tasks()
    assert len(tasks) == 10
    for task in tasks:
        assert {"id", "task", "expected_tool", "expected_contains"} <= set(task)


def test_evaluate_all_tasks_pass_offline():
    results = evaluate()
    assert len(results) == 10
    failures = [r["id"] for r in results if not r["passed"]]
    assert not failures, f"golden tasks failed: {failures}"


def test_report_renders(tmp_path):
    results = evaluate()
    report = render_report(results)
    assert "10/10 tasks passed" in report
    path = tmp_path / "eval_report.md"
    path.write_text(report, encoding="utf-8")
    assert path.exists()
