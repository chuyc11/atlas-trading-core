from trading_core.storage.file_paths import project_paths
from trading_core.storage.jsonl_store import read_json, read_jsonl, write_json, write_jsonl
from trading_core.storage.schema_validator import validate_record


def test_json_and_jsonl_round_trip(tmp_path) -> None:
    json_path = tmp_path / "sample.json"
    jsonl_path = tmp_path / "sample.jsonl"

    write_json(json_path, {"ok": True})
    write_jsonl(jsonl_path, [{"a": 1}, {"b": 2}])

    assert read_json(json_path)["ok"] is True
    assert read_jsonl(jsonl_path) == [{"a": 1}, {"b": 2}]


def test_date_paths_are_file_backed(tmp_path) -> None:
    paths = project_paths(tmp_path)
    assert paths.dated_jsonl("signals", "trading_signals", "2026-06-23").as_posix().endswith(
        "work/trading-core/data/signals/trading_signals-2026-06-23.jsonl"
    )


def test_schema_validator_checks_required_fields() -> None:
    validate_record(
        {
            "signal_id": "S1",
            "date": "2026-06-23",
            "strategy_id": "macro",
            "account_id": "CHINA_PAPER",
            "symbol": "510300.SH",
            "side": "LONG",
            "target_weight": 0.05,
            "confidence": 0.6,
            "status": "candidate",
        },
        project_paths().workspace_root / "work" / "shared" / "schemas" / "trading_signal.schema.json",
    )
