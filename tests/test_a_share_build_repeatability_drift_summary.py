from trading_core.equity_build_repeatability.drift_summary import build_repeatability_drift_summary


def test_repeatability_drift_summary_blocks_business_drift():
    result = build_repeatability_drift_summary(
        as_of_date="2026-06-26",
        comparison={"business_output_drift_count": 1, "blocking_reasons": []},
        protected_check={"protected_path_modifications_detected": False},
    )
    assert result["overall_status"] == "failed"

