from tests.a_share_ops_center_test_utils import build_ops_artifacts
from tests.a_share_owner_dashboard_test_utils import make_paths


def test_ops_release_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    _, audit = build_ops_artifacts(paths)
    boundary = audit["boundary"]
    assert boundary["run_daily_called"] is False
    assert boundary["old_run_daily_called"] is False
    assert boundary["day2_executed"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["ops_used_as_trade_instruction"] is False
