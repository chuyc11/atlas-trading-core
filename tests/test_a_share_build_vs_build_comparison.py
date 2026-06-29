from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_build_repeatability.artifact_snapshot import build_artifact_snapshot
from trading_core.equity_build_repeatability.build_comparison import build_build_vs_build_comparison


def test_build_vs_build_timestamp_drift_non_blocking(tmp_path):
    paths = make_paths(tmp_path)
    path = paths.data_dir / "equity_workflows" / "daily" / AS_OF_DATE / "workflow_summary.json"
    write_json(path, {"generated_at": "a", "value": 1})
    first = build_artifact_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_id="first")
    write_json(path, {"generated_at": "b", "value": 1})
    second = build_artifact_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_id="second")
    comparison = build_build_vs_build_comparison(paths=paths, as_of_date=AS_OF_DATE, first_snapshot=first, second_snapshot=second, protected_check={"protected_path_modifications_detected": False})
    assert comparison["timestamp_only_drift_count"] == 1
    assert comparison["blocking_reasons"] == []


def test_build_vs_build_business_drift_blocks(tmp_path):
    paths = make_paths(tmp_path)
    first = {"entries": [{"artifact_id": "x", "path": "data/equity_scores/daily/2026-06-26/x.parquet", "required": True, "sha256": "1", "stage": "scores"}], "artifact_count": 1}
    second = {"entries": [{"artifact_id": "x", "path": "data/equity_scores/daily/2026-06-26/x.parquet", "required": True, "sha256": "2", "stage": "scores"}], "artifact_count": 1}
    comparison = build_build_vs_build_comparison(paths=paths, as_of_date=AS_OF_DATE, first_snapshot=first, second_snapshot=second, protected_check={"protected_path_modifications_detected": False})
    assert "business_output_drift" in comparison["blocking_reasons"]

