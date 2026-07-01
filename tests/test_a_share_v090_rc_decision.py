from trading_core.equity_owner_v090_rc.rc_decision import build_release_candidate_decision


def test_v090_rc_decision_passes_only_with_required_checks():
    ok = {"overall_passed": True, "full_pytest_run": True}
    sweep = {"audit_sweep_passed": True}
    boundary = {"boundary_sweep_passed": True}
    trace = {"source_trace_sweep_passed": True}
    docs = {"documentation_freeze_passed": True}
    disclosure = {"overall_passed": True, "blocked_state_misrepresented_as_acceptable": False}
    decision = build_release_candidate_decision(full_pytest=ok, audit_sweep=sweep, boundary_sweep=boundary, source_trace_sweep=trace, documentation_freeze=docs, disclosure=disclosure)
    assert decision["decision"] == "v090_rc_passed_with_known_blocked_owner_readiness"
    bad = build_release_candidate_decision(full_pytest={"overall_passed": False, "full_pytest_run": True}, audit_sweep=sweep, boundary_sweep=boundary, source_trace_sweep=trace, documentation_freeze=docs, disclosure=disclosure)
    assert bad["decision"] == "v090_rc_blocked_by_regression"
