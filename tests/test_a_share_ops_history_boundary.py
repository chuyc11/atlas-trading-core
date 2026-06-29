from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_ops_history.ops_history_boundary import build_ops_history_boundary_check


def test_ops_history_boundary_blocks_commands(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_ops_history_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[], commands_executed=["run-daily"])
    assert boundary["overall_passed"] is False
    assert "commands_executed_not_empty" in boundary["blocking_reasons"]

