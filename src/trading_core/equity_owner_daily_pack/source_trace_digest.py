"""Source trace digest."""

from __future__ import annotations

from trading_core.equity_owner_daily_pack.daily_pack_config import TARGET_VERSION
from trading_core.equity_owner_daily_pack.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_source_trace_digest(*, paths: ProjectPaths, as_of_date: str) -> dict:
    ops_trace = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / as_of_date / "build_output_ops_source_trace.json")
    dash_trace = load_json(paths.data_dir / "equity_build_output_dashboard" / "daily" / as_of_date / "build_output_dashboard_source_trace.json")
    return {
        "digest_id": "A-SHARE-SOURCE-TRACE-DIGEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "ops_source_trace_complete": ops_trace.get("source_trace_complete", False),
        "dashboard_source_trace_complete": dash_trace.get("source_trace_complete", False),
        "ops_source_entry_count": len(ops_trace.get("entries", [])),
        "dashboard_source_entry_count": len(dash_trace.get("entries", [])),
    }

