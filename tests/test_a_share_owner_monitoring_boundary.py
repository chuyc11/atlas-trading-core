from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_owner_monitoring.monitoring_boundary import build_monitoring_boundary_check


def test_monitoring_boundary_defaults_are_clean(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_monitoring_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is True
    assert boundary["alert_used_as_trade_instruction"] is False
