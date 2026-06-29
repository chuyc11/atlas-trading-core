from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_build_repeatability.artifact_snapshot import build_artifact_snapshot


def test_build_artifact_snapshot_generates_entries(tmp_path):
    paths = make_paths(tmp_path)
    write_json(paths.data_dir / "equity_workflows" / "daily" / AS_OF_DATE / "workflow_summary.json", {"generated_at": "x", "value": 1})
    result = build_artifact_snapshot(paths=paths, as_of_date=AS_OF_DATE, snapshot_id="test")
    assert result["artifact_count"] == 1
    assert result["entries"][0]["normalized_sha256"]

