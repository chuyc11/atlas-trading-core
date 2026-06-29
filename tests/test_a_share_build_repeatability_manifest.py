from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_repeatability.repeatability_manifest import build_repeatability_manifest


def test_repeatability_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    result = build_repeatability_manifest(
        as_of_date=AS_OF_DATE,
        mode="run_repeat_build_from_existing_data",
        execution_record={"command_executed": True},
        workflow_result={"workflow_audit_overall_passed": True},
        comparison={"comparison_completed": True},
        drift_summary={},
        protected_check={"protected_path_modifications_detected": False},
        source_trace={"source_trace_complete": True},
        boundary={"blocking_reasons": [], "old_run_daily_called": False, "broker_connected": False, "real_orders_placed": False, "buy_sell_signals_generated": False, "order_preview_generated": False},
        output_artifacts={},
        source_artifacts={},
        paths=paths,
    )
    assert result["manifest_id"] == "A-SHARE-BUILD-REPEATABILITY-MANIFEST"
    assert result["overall_repeatability_status"] == "passed"

