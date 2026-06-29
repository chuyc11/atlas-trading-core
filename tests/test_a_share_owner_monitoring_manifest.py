from trading_core.equity_owner_monitoring.monitoring_manifest import build_monitoring_manifest


def test_monitoring_manifest_records_next_version():
    manifest = build_monitoring_manifest(as_of_date="2026-06-26", generated_at="now", mode="build_monitoring_dashboard", monitoring_status_card={"overall_monitoring_status": "passed", "run_history_observation_count": 1, "trend_analysis_available": False, "critical_alert_count": 0, "warning_alert_count": 0, "blocking_count": 0}, output_artifacts={}, source_artifacts={}, boundary={"overall_passed": True})
    assert manifest["recommended_next_version"].startswith("v0.8.4")
    assert manifest["trend_analysis_available"] is False
