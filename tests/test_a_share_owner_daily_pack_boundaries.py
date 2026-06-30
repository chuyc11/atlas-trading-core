from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs
from trading_core.equity_owner_daily_pack.input_availability import load_json


def test_owner_daily_pack_does_not_rerun_or_touch_trading_boundaries(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)

    boundary = load_json(paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE / "daily_pack_boundary_check.json")

    assert boundary["rerun_build_from_existing_data"] is False
    assert boundary["rerun_ops_refresh"] is False
    assert boundary["public_network_refresh_run"] is False
    assert boundary["full_research_run"] is False
    assert boundary["execute_remediation_actions"] is False
    assert boundary["external_notifications_sent"] is False
    assert boundary["old_run_daily_called"] is False
    assert boundary["day2_executed"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["daily_pack_used_as_trade_instruction"] is False


def test_owner_daily_pack_forbidden_wording_blocks_boundary(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)
    out = paths.outputs_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE
    (out / "BUY_LIST.md").write_text("推荐买入", encoding="utf-8")

    from trading_core.equity_owner_daily_pack.daily_pack_audit import audit_a_share_owner_daily_pack

    audit = audit_a_share_owner_daily_pack(as_of_date=AS_OF_DATE, paths=paths)

    assert audit["overall_passed"] is False
    assert "forbidden_artifacts_absent" in audit["blocking_reasons"]
