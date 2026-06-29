from tests.a_share_owner_dashboard_test_utils import make_paths
from trading_core.equity_owner_remediation.remediation_boundary import build_remediation_boundary_check


def test_remediation_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_remediation_boundary_check(paths=paths, as_of_date="2026-06-26", warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is True
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["remediation_used_as_trade_instruction"] is False
