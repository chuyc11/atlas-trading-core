from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day.workflow_plan import build_current_day_workflow_plan


def test_current_day_workflow_plan_uses_new_workflow_cli(tmp_path):
    paths = make_paths(tmp_path)
    plan = build_current_day_workflow_plan(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE, workflow_mode="validate_existing_artifacts")
    assert "run-and-audit-a-share-daily-research-workflow" in plan["workflow_command"]
    assert "run-daily" not in plan["workflow_command"]
    assert plan["post_workflow_modules_enabled"] is False

