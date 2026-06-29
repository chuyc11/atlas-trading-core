from trading_core.equity_ops_history.ops_history_manifest import build_ops_history_manifest, build_ops_history_summary


def test_ops_history_manifest_and_summary_record_insufficient_status():
    manifest = build_ops_history_manifest(as_of_date="2026-06-26", generated_at="now", mode="build_trend_baselines", run_record={"source_version": "v0.8.5", "ops_health_score": 65}, append_result={"append_completed": True}, snapshot={"run_history_observation_count": 1}, trend_sufficiency={"trend_analysis_available": False, "baseline_status": "insufficient_history"}, boundary={"commands_executed": []}, output_artifacts={}, source_artifacts={})
    summary = build_ops_history_summary(as_of_date="2026-06-26", mode="build_trend_baselines", manifest=manifest, append_result={"append_completed": True, "idempotent_append": False})
    assert manifest["baseline_status"] == "insufficient_history"
    assert summary["run_history_observation_count"] == 1

