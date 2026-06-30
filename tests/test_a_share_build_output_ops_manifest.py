from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    manifest = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_manifest.json")
    summary = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_summary.json")
    assert manifest["manifest_id"] == "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-MANIFEST"
    assert summary["summary_id"] == "A-SHARE-BUILD-OUTPUT-OPS-REFRESH-SUMMARY"
    assert summary["recommended_next_version"] == "v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack"

