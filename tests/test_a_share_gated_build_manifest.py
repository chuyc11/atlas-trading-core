from trading_core.equity_current_day_builds.gated_build_manifest import build_gated_build_manifest, build_gated_build_summary


def test_gated_build_manifest_records_recommended_next_version(tmp_path):
    manifest = build_gated_build_manifest(as_of_date="2026-06-26", mode="run_gated_build_from_existing_data", preflight_gate={"overall_passed": True}, execution_record={"command_executed": True}, workflow_result={"workflow_audit_overall_passed": True}, comparison={"comparison_completed": True}, drift_summary={}, boundary={"blocking_reasons": [], "warnings": [], "overall_passed": True}, output_artifacts={}, source_artifacts={}, paths=type("P", (), {"project_root": tmp_path})())
    summary = build_gated_build_summary(as_of_date="2026-06-26", mode="run_gated_build_from_existing_data", manifest=manifest, preflight_gate={"overall_passed": True}, execution_record={"command_executed": True}, workflow_result={"workflow_audit_overall_passed": True}, comparison={"comparison_completed": True}, drift_summary={"overall_status": "clean"}, boundary={"overall_passed": True, "blocking_reasons": [], "warnings": []})
    assert manifest["recommended_next_version"].startswith("v0.8.8")
    assert summary["workflow_mode"] == "build_from_existing_data"

