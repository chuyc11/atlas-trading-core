from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_output_dashboard.build_output_manifest import build_manifest


def test_build_output_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    cards = {k: {"x": True} for k in ["build_output_executive_status_card", "build_output_data_freshness_card", "build_output_workflow_status_card", "build_output_research_output_card", "build_output_warning_and_blocker_card", "build_output_artifact_navigation", "build_output_candidate_summary_card", "build_output_portfolio_summary_card", "build_output_benchmark_summary_card", "build_output_performance_summary_card", "build_output_attribution_summary_card", "build_output_repeatability_card", "build_output_protected_path_card"]}
    cards["build_output_repeatability_card"] = {"repeatability_audit_passed": True, "business_output_drift_count": 0}
    cards["build_output_protected_path_card"] = {"protected_path_modifications_detected": False}
    manifest = build_manifest(as_of_date=AS_OF_DATE, mode="build_owner_dashboard_from_build_output", cards=cards, source_resolution={}, source_trace={"source_trace_complete": True}, boundary={"blocking_reasons": []}, output_artifacts={}, source_artifacts={}, paths=paths)
    assert manifest["manifest_id"] == "A-SHARE-BUILD-OUTPUT-OWNER-DASHBOARD-MANIFEST"

