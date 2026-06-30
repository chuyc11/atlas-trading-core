from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_history_boundary_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    boundary = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_history_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["owner_readiness_used_as_trade_instruction"] is False
