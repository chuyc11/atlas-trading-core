from trading_core.equity_ops_history.history_append import append_ops_run_history


def test_ops_history_append_is_idempotent(tmp_path):
    path = tmp_path / "history.json"
    record = {"run_record_id": "run", "as_of_date": "2026-06-26", "source_version": "v0.8.5", "manifest_sha256": "abc"}
    index, first = append_ops_run_history(history_path=path, run_record=record)
    index, second = append_ops_run_history(history_path=path, run_record=record)
    assert first["records_after"] == 1
    assert second["idempotent_append"] is True
    assert len(index["records"]) == 1

