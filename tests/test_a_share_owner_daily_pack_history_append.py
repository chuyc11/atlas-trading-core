from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths
from tests.a_share_owner_daily_pack_history_test_utils import seed_owner_daily_pack_history_inputs, seed_owner_daily_pack_history_outputs
from trading_core.equity_owner_daily_pack_history.daily_pack_history_builder import build_a_share_owner_daily_pack_history
from trading_core.equity_owner_daily_pack_history.history_append import append_daily_pack_history
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def test_owner_daily_pack_history_append_idempotent_duplicate(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_daily_pack_history_inputs(paths)
    first = build_a_share_owner_daily_pack_history(as_of_date=AS_OF_DATE, paths=paths)
    second = build_a_share_owner_daily_pack_history(as_of_date=AS_OF_DATE, paths=paths)
    assert first["daily_pack_history_observation_count"] == 1
    assert second["daily_pack_history_observation_count"] == 1
    assert second["idempotent_append"] is True


def test_owner_daily_pack_history_append_same_date_changed_warning(tmp_path):
    path = tmp_path / "history.json"
    record = {"run_record_id": "r", "as_of_date": AS_OF_DATE, "source_workflow_mode": "build_from_existing_data", "daily_pack_manifest_sha256": "a"}
    append_daily_pack_history(history_path=path, run_record=record)
    _, result = append_daily_pack_history(history_path=path, run_record={**record, "daily_pack_manifest_sha256": "b"})
    assert result["same_date_changed_content_warning"] is True
    assert result["records_after"] == 2
