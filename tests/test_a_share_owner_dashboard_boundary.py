from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_owner_dashboard.dashboard_boundary import build_dashboard_boundary_check


def test_boundary_passes_when_no_forbidden_artifacts_exist(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_dashboard_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is True
    assert boundary["broker_connected"] is False
