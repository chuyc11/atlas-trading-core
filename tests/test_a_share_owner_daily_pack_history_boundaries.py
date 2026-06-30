from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.daily_pack_history_audit import audit_a_share_owner_daily_pack_history
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_history_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    boundary = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_history_boundary_check.json")
    assert boundary["build_from_existing_data_rerun"] is False
    assert boundary["owner_daily_pack_rerun"] is False
    assert boundary["public_network_refresh_run"] is False
    assert boundary["full_research_run"] is False
    assert boundary["run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False


def test_owner_daily_pack_history_forbidden_wording_blocks_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    out = paths.outputs_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE
    (out / "BUY_LIST.md").write_text("推荐买入", encoding="utf-8")
    audit = audit_a_share_owner_daily_pack_history(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert "no_forbidden_artifacts" in audit["blocking_reasons"]
