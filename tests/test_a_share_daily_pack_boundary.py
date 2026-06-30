from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs
from trading_core.equity_owner_daily_pack.input_availability import load_json


def test_daily_pack_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)

    boundary = load_json(paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "daily_pack_boundary_check.json")

    assert boundary["overall_passed"] is True
    assert boundary["run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["daily_pack_used_as_trade_instruction"] is False
