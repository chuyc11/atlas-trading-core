from trading_core.equity_current_day_builds.warning_summary import build_gated_build_warning_summary


def test_gated_build_warning_summary_carries_forward_sources():
    summary = build_gated_build_warning_summary(as_of_date="2026-06-26", input_availability={"warnings": ["a"]}, date_alignment={"warnings": []}, preflight_gate={"warnings": ["b"]}, execution_record={"warnings": []}, comparison={"warnings": []}, drift_summary={"warnings": []})
    assert summary["total_warnings"] == 2

