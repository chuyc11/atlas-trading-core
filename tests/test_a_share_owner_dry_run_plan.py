from trading_core.equity_owner_remediation.dry_run_plan import build_dry_run_remediation_plan


def test_dry_run_plan_does_not_execute_commands():
    plan = build_dry_run_remediation_plan(
        as_of_date="2026-06-26",
        checklist={"items": [{"item_id": "x", "safe_action_type": "verify_audit", "manual_review_required": True, "command_if_any": "python -m trading_core.cli audit"}]},
    )
    assert plan["dry_run_only"] is True
    assert plan["commands_to_review"]
    assert plan["commands_executed"] == []
    assert plan["execute_remediation_actions"] is False
