from trading_core.equity_owner_v0820_gate_outcome.preservation_checks import build_boundary_preservation_check, build_threshold_preservation_check, build_waiver_exclusion_check


def test_v0820_preservation_checks_keep_threshold_waiver_and_boundary():
    threshold = build_threshold_preservation_check(availability={"minimum_owner_readiness_score": 75})
    waiver = build_waiver_exclusion_check()
    boundary = build_boundary_preservation_check()
    assert threshold["threshold_lowered"] is False
    assert threshold["threshold_preserved"] is True
    assert waiver["waiver_used_for_outcome"] is False
    assert boundary["broker_connected"] is False
    assert boundary["buy_sell_signals_generated"] is False

