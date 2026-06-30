from tests.a_share_owner_readiness_gate_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_gate_outputs
from trading_core.equity_owner_readiness_gate.gate_boundary import build_boundary_check


def test_owner_readiness_gate_no_forbidden_runtime_boundaries(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_outputs(paths)
    boundary = build_boundary_check(paths=paths, as_of_date=AS_OF_DATE)
    assert boundary["public_network_refresh_run"] is False
    assert boundary["full_research_run"] is False
    assert boundary["run_daily_called"] is False
    assert boundary["old_run_daily_called"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["order_preview_generated"] is False
    assert boundary["overall_passed"] is True


def test_owner_readiness_gate_forbidden_wording_blocks_boundary(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_outputs(paths)
    out = paths.outputs_dir / "equity_owner_readiness_gate" / "daily" / AS_OF_DATE
    (out / "BAD.md").write_text("推荐买入", encoding="utf-8")
    boundary = build_boundary_check(paths=paths, as_of_date=AS_OF_DATE)
    assert boundary["overall_passed"] is False
    assert "forbidden_positive_wording_present" in boundary["blocking_reasons"]
