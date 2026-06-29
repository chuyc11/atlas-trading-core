from trading_core.equity_ops_center.action_summary import build_ops_action_summary


def test_ops_action_summary_automatic_zero():
    summary = build_ops_action_summary(
        as_of_date="2026-06-26",
        payloads={"safe_owner_action_checklist": {"safe_action_count": 1, "automatic_action_count": 0, "items": [{"item_id": "x", "title_zh": "检查", "safe_action_type": "verify_audit", "manual_review_required": True}]}},
    )
    assert summary["automatic_action_count"] == 0
    assert summary["manual_review_count"] == 1
    assert summary["forbidden_action_hits"] == []
