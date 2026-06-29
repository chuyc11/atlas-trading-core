from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths, seed_build_output_dashboard_outputs
from trading_core.equity_build_output_dashboard.build_output_dashboard_audit import audit_a_share_build_output_owner_dashboard


def test_build_output_dashboard_boundaries_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_dashboard_outputs(paths)
    audit = audit_a_share_build_output_owner_dashboard(as_of_date=AS_OF_DATE, paths=paths)
    boundary = audit["boundary"]
    assert boundary["old_run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["dashboard_used_as_trade_instruction"] is False
