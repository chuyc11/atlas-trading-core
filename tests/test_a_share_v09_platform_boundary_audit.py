from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import audit_a_share_v09_platform, run_a_share_v09_daily_platform


def test_v09_platform_boundary_and_audit_pass(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    audit = audit_a_share_v09_platform(paths=paths, as_of_date=AS_OF_DATE)
    boundary = platform_json(paths, "v09_platform_boundary_check")

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["artifact_checks"]["json_count"] == 17
    assert audit["artifact_checks"]["markdown_count"] == 5
    assert boundary["protected_paths_untouched"] is True
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["real_order_preview_generated"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["owner_readiness_gate_rerun"] is False
    assert boundary["new_gate_score_generated"] is False
    assert boundary["new_gate_decision_generated"] is False
