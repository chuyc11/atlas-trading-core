from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    boundary = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["build_from_existing_data_rerun"] is False
    assert boundary["public_network_refresh_run"] is False
    assert boundary["full_research_run"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["execute_remediation_actions"] is False
    assert boundary["external_notifications_sent"] is False
    assert boundary["ops_refresh_used_as_trade_instruction"] is False

