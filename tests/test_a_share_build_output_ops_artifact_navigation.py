from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_artifact_navigation_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    payload = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_artifact_navigation.json")
    ids = {entry["artifact_id"] for entry in payload["entries"]}
    assert "build_output_ops_summary" in ids
    assert "build_output_ops_refresh_report" in ids

