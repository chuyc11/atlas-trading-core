from trading_core.equity_ops_center.ops_plan import build_ops_plan, forbidden_command_hits


def test_ops_plan_aggregate_only_behavior_and_forbidden_detection():
    plan = build_ops_plan(as_of_date="2026-06-26", mode="aggregate_existing_ops_artifacts")
    assert plan["commands_executed"] == []
    assert plan["execution_policy"] == "aggregate_existing_artifacts_only"
    assert forbidden_command_hits(["python -m trading_core.cli run-daily 2026-06-26"])
