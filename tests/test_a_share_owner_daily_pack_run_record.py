from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_run_record_created(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    record = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_run_record.json")
    assert record["run_record_id"] == f"A-SHARE-OWNER-DAILY-PACK-{AS_OF_DATE}"
    assert record["daily_pack_audit_passed"] is True
    assert record["daily_pack_manifest_sha256"]
    assert record["daily_pack_used_as_trade_instruction"] is False
