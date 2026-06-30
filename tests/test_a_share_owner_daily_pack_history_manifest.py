from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_history_manifest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    manifest = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_history_manifest.json")
    summary = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_history_summary.json")
    assert manifest["manifest_id"] == "A-SHARE-OWNER-DAILY-PACK-HISTORY-MANIFEST"
    assert summary["summary_id"] == "A-SHARE-OWNER-DAILY-PACK-HISTORY-SUMMARY"
