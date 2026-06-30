from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_history_snapshot_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_outputs(paths)
    snapshot = load_json(paths.data_dir / "equity_owner_daily_pack_history" / "daily" / AS_OF_DATE / "daily_pack_history_snapshot.json")
    assert snapshot["daily_pack_history_observation_count"] == 1
    assert snapshot["trend_analysis_available"] is False
    assert snapshot["synthetic_history_used"] is False
