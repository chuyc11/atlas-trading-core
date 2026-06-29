from trading_core.equity_ops_center.health_score import build_ops_health_score_card, grade_for_score


def test_ops_health_score_deterministic_and_grade_mapping():
    card = build_ops_health_score_card(as_of_date="2026-06-26", required_modules_passed=True, issue_summary={"blocking_issue_count": 0, "warning_issue_count": 10, "known_non_blocking_issue_count": 5})
    assert card["score"] == 65
    assert card["grade"] == "C"
    assert grade_for_score(95) == "A"
    assert grade_for_score(80) == "B"
    assert grade_for_score(50) == "D"
    assert grade_for_score(20) == "F"
