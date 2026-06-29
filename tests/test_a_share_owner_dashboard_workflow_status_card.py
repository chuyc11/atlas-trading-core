from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.workflow_status_card import build_workflow_status_card


def test_workflow_status_card_keeps_execution_boundary_false(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    card = build_workflow_status_card(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE)
    assert card["workflow_audit_passed"] is True
    assert card["old_run_daily_called"] is False
    assert card["day2_executed"] is False
