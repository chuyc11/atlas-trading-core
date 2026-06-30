"""Daily pack run record."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_owner_daily_pack_history.daily_pack_history_config import BASELINE_VERSION, TARGET_VERSION
from trading_core.system.common import relative


def build_daily_pack_run_record(*, paths, as_of_date: str, input_paths: dict[str, Path], payloads: dict[str, Any], readiness_score: dict[str, Any]) -> dict[str, Any]:
    manifest_path = input_paths["daily_pack_manifest"]
    audit_path = input_paths["owner_daily_pack_audit"]
    status = payloads["owner_daily_status_brief"]
    audit = payloads["owner_daily_pack_audit"]
    boundary = payloads["daily_pack_boundary_check"]
    return {
        "run_record_id": f"A-SHARE-OWNER-DAILY-PACK-{as_of_date}",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_version": BASELINE_VERSION,
        "source_workflow_mode": "build_from_existing_data",
        "daily_pack_audit_passed": audit.get("overall_passed") is True,
        "daily_pack_audit_path": relative(audit_path, paths.project_root),
        "daily_pack_manifest_path": relative(manifest_path, paths.project_root),
        "daily_pack_manifest_sha256": sha256_file(manifest_path),
        "overall_status": status.get("overall_status"),
        "owner_readiness_score": readiness_score["score"],
        "owner_readiness_grade": readiness_score["grade"],
        "blocking_count": int(status.get("blocking_count", 0) or 0),
        "warning_count": int(status.get("warning_count", 0) or 0),
        "safe_action_count": int(status.get("safe_action_count", 0) or 0),
        "automatic_action_count": int(status.get("automatic_action_count", 0) or 0),
        "business_output_drift_count": int(status.get("business_output_drift_count", 0) or 0),
        "protected_path_modifications_detected": status.get("protected_path_modifications_detected") is True,
        "boundary_clean": boundary.get("overall_passed") is True and not boundary.get("blocking_reasons"),
        "not_investment_decision_pack": payloads["daily_pack_summary"].get("not_investment_decision_pack") is True,
        "daily_pack_used_as_trade_instruction": boundary.get("daily_pack_used_as_trade_instruction") is True,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
