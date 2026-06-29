"""Executive status card for owner dashboard."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_owner_dashboard.dashboard_config import DASHBOARD_FLAGS, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


def build_executive_status_card(
    *,
    as_of_date: str,
    resolved_as_of_date: str,
    input_availability: dict[str, Any],
    data_freshness_card: dict[str, Any],
    workflow_status_card: dict[str, Any],
    research_output_card: dict[str, Any],
    performance_summary_card: dict[str, Any],
    attribution_summary_card: dict[str, Any],
    warning_and_blocker_card: dict[str, Any],
) -> dict[str, Any]:
    blocking_count = int(warning_and_blocker_card.get("blocking_count", 0))
    warning_count = int(warning_and_blocker_card.get("warning_count", 0))
    optional_missing = any(
        row.get("status") == "missing_optional"
        for row in research_output_card.get("outputs", [])
    )
    if blocking_count:
        overall = "failed"
    elif optional_missing:
        overall = "partial"
    elif warning_count:
        overall = "passed_with_warnings"
    else:
        overall = "passed"
    return {
        "card_id": "EXECUTIVE_STATUS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "overall_status": overall,
        "status_label_zh": {"passed": "通过", "passed_with_warnings": "通过但有提示", "failed": "未通过", "blocked": "阻断", "partial": "部分可用"}[overall],
        "data_refresh_status": "passed" if data_freshness_card.get("data_refresh_audit_passed") else "failed",
        "workflow_status": "passed" if workflow_status_card.get("workflow_audit_passed") else "failed",
        "briefing_status": research_output_card.get("briefing_status", "missing_required"),
        "tracking_status": research_output_card.get("tracking_status", "missing_required"),
        "benchmark_status": research_output_card.get("benchmark_status", "missing_optional"),
        "performance_status": performance_summary_card.get("status", "missing_optional"),
        "attribution_status": attribution_summary_card.get("status", "missing_optional"),
        "blocking_count": blocking_count,
        "warning_count": warning_count,
        "critical_warning_count": int(warning_and_blocker_card.get("critical_warning_count", 0)),
        "input_availability_passed": input_availability.get("overall_passed") is True,
        **DASHBOARD_FLAGS,
    }


def build_provider_health_card(*, paths: ProjectPaths | None, as_of_date: str, resolved_as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    provider_health_path = paths.data_dir / "equity_data_refresh" / "daily" / resolved_as_of_date / "provider_health_check.json"
    provider_health = _load_json(provider_health_path)
    providers = []
    for row in provider_health.get("providers", []):
        providers.append(
            {
                "provider_id": row.get("provider_id"),
                "enabled": bool(row.get("enabled")),
                "reachable": row.get("reachable"),
                "local_source_available": row.get("local_source_available"),
                "supports_required_dataset": row.get("supports_required_dataset"),
                "current_attempt_status": row.get("current_attempt_status"),
                "fallback_used": bool(row.get("fallback_used")),
                "error_type": row.get("error_type"),
            }
        )
    enabled = [row for row in providers if row["enabled"]]
    disabled = [row for row in providers if not row["enabled"]]
    fallback_used = [row["provider_id"] for row in providers if row["fallback_used"]]
    return {
        "card_id": "PROVIDER_HEALTH",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "resolved_as_of_date": resolved_as_of_date,
        "status": "available" if providers else "missing_optional",
        "provider_health_path": str(provider_health_path),
        "provider_count": len(providers),
        "enabled_provider_count": len(enabled),
        "disabled_provider_count": len(disabled),
        "enabled_providers": [row["provider_id"] for row in enabled],
        "disabled_providers": [row["provider_id"] for row in disabled],
        "fallback_used": fallback_used,
        "network_providers_disabled": all((not row["enabled"]) for row in providers if row["provider_id"] in {"eastmoney_public_provider", "akshare_provider"}),
        "warnings": [] if providers else ["provider_health_check_missing"],
    }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
