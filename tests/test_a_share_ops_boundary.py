from tests.a_share_owner_dashboard_test_utils import make_paths
from trading_core.equity_ops_center.ops_boundary import build_ops_boundary_check


def test_ops_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_ops_boundary_check(paths=paths, as_of_date="2026-06-26", warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is True
    assert boundary["old_run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["ops_used_as_trade_instruction"] is False
