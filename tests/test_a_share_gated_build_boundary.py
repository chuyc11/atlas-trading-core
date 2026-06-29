from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day_builds.gated_build_boundary import build_gated_build_boundary_check


def test_gated_build_boundary_blocks_broker_violation(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_gated_build_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[], execution_record={"broker_connected": True})
    assert boundary["overall_passed"] is False
    assert "broker_connected" in boundary["blocking_reasons"]

