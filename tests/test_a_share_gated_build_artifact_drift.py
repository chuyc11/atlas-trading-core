from trading_core.equity_current_day_builds.artifact_drift import build_artifact_drift_summary


def test_gated_build_artifact_drift_marks_boundary_blocking():
    drift = build_artifact_drift_summary(paths=None, as_of_date="2026-06-26", comparison={"blocking_reasons": ["build_boundary_failed"], "warnings": []})
    assert "boundary_drift_detected" in drift["blocking_reasons"]

