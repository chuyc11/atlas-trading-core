"""Append-only daily pack history index."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import write_json
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack_history.input_availability import load_json


def append_daily_pack_history(*, history_path: Path, run_record: dict[str, Any], allow_rebuild_history: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    existing = load_json(history_path)
    records = [] if allow_rebuild_history else list(existing.get("records", []))
    before = len(records)
    key = _dedupe_key(run_record)
    duplicate = next((row for row in records if _dedupe_key(row) == key), None)
    same_date_changed = any(row.get("as_of_date") == run_record.get("as_of_date") and _dedupe_key(row) != key for row in records)
    warnings = ["same_date_changed_content_warning"] if same_date_changed else []
    if duplicate is None:
        record = {**run_record, "run_sequence": before + 1, "history_record_id": f"{run_record['run_record_id']}-{before + 1:03d}"}
        records.append(record)
    index = {
        "index_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-INDEX",
        "target_version": TARGET_VERSION,
        "append_only_history": True,
        "dedupe_key": ["as_of_date", "source_workflow_mode", "daily_pack_manifest_sha256"],
        "records": records,
    }
    write_json(history_path, index)
    return index, {
        "append_result_id": "A-SHARE-OWNER-DAILY-PACK-HISTORY-APPEND-RESULT",
        "target_version": TARGET_VERSION,
        "append_attempted": True,
        "append_completed": True,
        "idempotent_append": duplicate is not None,
        "duplicate_detected": duplicate is not None,
        "same_date_changed_content_warning": same_date_changed,
        "records_before": before,
        "records_after": len(records),
        "blocking_reasons": [],
        "warnings": warnings,
    }


def _dedupe_key(record: dict[str, Any]) -> tuple[Any, Any, Any]:
    return (record.get("as_of_date"), record.get("source_workflow_mode"), record.get("daily_pack_manifest_sha256"))
