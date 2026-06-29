from trading_core.equity_ops_center.ops_report import render_command_center, render_compact


def test_ops_reports_generated_and_compact_length():
    payload = {
        "ops_summary": {"overall_status": "passed", "blocking_issue_count": 0, "warning_issue_count": 0, "known_non_blocking_issue_count": 0, "safe_action_count": 0, "automatic_action_count": 0, "ops_health_score": 100, "ops_health_grade": "A"},
        "ops_health_score_card": {"score": 100, "grade": "A"},
        "ops_boundary_check": {"overall_passed": True},
        "ops_module_status_matrix": {"rows": []},
    }
    assert "今日 Ops 总览" in render_command_center(payload)
    assert len(render_compact(payload)) <= 1200
