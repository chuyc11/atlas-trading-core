from tests.a_share_owner_dashboard_test_utils import make_paths
from tests.a_share_owner_remediation_test_utils import build_remediation_artifacts


def test_owner_remediation_boundary_release_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    _, audit = build_remediation_artifacts(paths)
    boundary = audit["boundary"]
    assert boundary["old_run_daily_called"] is False
    assert boundary["day2_executed"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["remediation_used_as_trade_instruction"] is False
