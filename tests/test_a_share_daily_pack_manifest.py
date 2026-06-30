from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_test_utils import seed_owner_daily_pack_outputs
from trading_core.equity_owner_daily_pack.input_availability import load_json


def test_daily_pack_manifest_and_summary_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_outputs(paths)
    base = paths.data_dir / "equity_owner_daily_pack" / "daily" / AS_OF_DATE

    manifest = load_json(base / "daily_pack_manifest.json")
    summary = load_json(base / "daily_pack_summary.json")

    assert manifest["manifest_id"] == "A-SHARE-OWNER-DAILY-PACK-MANIFEST"
    assert summary["summary_id"] == "A-SHARE-OWNER-DAILY-PACK-SUMMARY"
    assert summary["recommended_next_version"] == "v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends"
