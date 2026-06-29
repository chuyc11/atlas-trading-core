from trading_core.equity_owner_remediation.action_checklist import build_safe_owner_action_checklist, validate_checklist


def test_safe_action_checklist_generation():
    checklist = build_safe_owner_action_checklist(as_of_date="2026-06-26", issue_catalog={"issue_count": 1, "issues": []})
    assert checklist["safe_action_count"] == 8
    assert checklist["automatic_action_count"] == 0
    assert all(item["allowed_to_execute_automatically"] is False for item in checklist["items"])


def test_forbidden_action_type_rejected():
    assert validate_checklist([{"item_id": "x", "safe_action_type": "place_order", "allowed_to_execute_automatically": False}])
