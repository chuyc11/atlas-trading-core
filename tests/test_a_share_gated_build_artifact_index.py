from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_current_day_builds.artifact_index import build_gated_build_artifact_index


def test_gated_build_artifact_index_lists_current_day_json(tmp_path):
    paths = make_paths(tmp_path)
    write_json(paths.data_dir / "equity_current_day_runs" / "daily" / AS_OF_DATE / "current_day_run_manifest.json", {})
    index = build_gated_build_artifact_index(paths=paths, as_of_date=AS_OF_DATE, workflow_result={"status": "passed"})
    assert index["artifact_count"] == 1

