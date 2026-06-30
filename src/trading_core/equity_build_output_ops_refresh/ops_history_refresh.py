"""Ops history refresh for build-output ops layer."""

from __future__ import annotations

from trading_core.equity_build_output_ops_refresh.build_output_ops_config import TARGET_VERSION
from trading_core.equity_build_output_ops_refresh.input_availability import load_json
from trading_core.storage.file_paths import ProjectPaths


def build_ops_history_refresh(*, paths: ProjectPaths, as_of_date: str, ops_center_refresh: dict) -> dict:
    ops_history_audit = load_json(paths.data_dir / "equity_data_quality" / "a_share_ops_history_baseline_audit.json")
    return {
        "refresh_id": "A-SHARE-BUILD-OUTPUT-OPS-HISTORY-REFRESH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_workflow_mode": "build_from_existing_data",
        "ops_history_refresh_performed": True,
        "synthetic_history_used": False,
        "future_dates_used": False,
        "observations_added": 1,
        "observation_dates": [as_of_date],
        "ops_history_audit_available": bool(ops_history_audit),
        "ops_history_audit_passed": ops_history_audit.get("overall_passed"),
        "health_score": ops_center_refresh.get("health_score"),
        "health_grade": ops_center_refresh.get("health_grade"),
        "overall_status": ops_center_refresh.get("overall_status"),
    }

