"""Input availability for owner dashboard."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trading_core.equity_current_day.current_day_config import current_day_artifact_paths
from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.equity_owner_dashboard.dashboard_config import TARGET_VERSION
from trading_core.equity_workflows.workflow_config import workflow_artifact_paths
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths, relative


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}


def load_list(path: Path) -> list[Any]:
    if not path.exists():
        return []
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def artifact_record(paths: ProjectPaths, path: Path, *, label_zh: str = "", category: str = "", owner_priority: str = "diagnostic") -> dict[str, Any]:
    return {
        "artifact_id": path.stem,
        "label_zh": label_zh or path.stem,
        "category": category,
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
        "owner_priority": owner_priority,
    }


def input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, dict[str, Path]]:
    current = current_day_artifact_paths(paths, as_of_date)
    refresh = data_refresh_artifact_paths(paths, as_of_date)
    workflow = workflow_artifact_paths(paths, as_of_date)
    return {
        "current_day_run": {
            "source": current["current_day_run_manifest"],
            "audit": current["current_day_audit_json"],
            "summary": current["current_day_summary"],
            "report": current["current_day_summary_report"],
        },
        "data_refresh": {
            "source": refresh["data_refresh_summary"],
            "audit": refresh["data_refresh_audit_json"],
            "freshness": refresh["dataset_freshness_validation"],
            "coverage": refresh["dataset_coverage_summary"],
            "provider": refresh["provider_health_check"],
            "gaps": refresh["data_gap_report"],
        },
        "workflow": {
            "source": workflow["workflow_summary"],
            "audit": workflow["workflow_audit_json"],
            "run_manifest": workflow["workflow_run_manifest"],
            "stage_manifest": workflow["workflow_stage_manifest"],
        },
        "daily_briefing": {
            "source": paths.data_dir / "equity_briefings" / "daily" / as_of_date / "daily_stock_selection_briefing.json",
            "report": paths.outputs_dir / "equity_briefings" / "daily" / as_of_date / "DAILY_STOCK_SELECTION_BRIEFING.md",
            "audit": paths.data_dir / "equity_data_quality" / "a_share_daily_stock_selection_briefing_audit.json",
        },
        "portfolio_tracking": {
            "source": paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "tracking_summary.json",
            "nav": paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "portfolio_nav_snapshot.json",
            "report": paths.outputs_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md",
            "audit": paths.data_dir / "equity_data_quality" / "a_share_virtual_portfolio_tracking_audit.json",
        },
        "benchmark": {
            "source": paths.data_dir / "equity_benchmarks" / "daily" / as_of_date / "benchmark_summary.json",
            "report": paths.outputs_dir / "equity_benchmarks" / "daily" / as_of_date / "A_SHARE_BENCHMARK_SUMMARY.md",
            "audit": paths.data_dir / "equity_data_quality" / "a_share_benchmark_comparison_audit.json",
        },
        "performance": {
            "source": paths.data_dir / "equity_performance" / "daily" / as_of_date / "performance_summary.json",
            "report": paths.outputs_dir / "equity_performance" / "daily" / as_of_date / "A_SHARE_MULTI_DAY_PERFORMANCE_SUMMARY.md",
            "audit": paths.data_dir / "equity_data_quality" / "a_share_multi_day_performance_audit.json",
        },
        "attribution": {
            "source": paths.data_dir / "equity_attribution" / "daily" / as_of_date / "attribution_summary.json",
            "report": paths.outputs_dir / "equity_attribution" / "daily" / as_of_date / "A_SHARE_ATTRIBUTION_SUMMARY.md",
            "audit": paths.data_dir / "equity_data_quality" / "a_share_performance_attribution_audit.json",
        },
    }


def build_dashboard_input_availability(*, paths: ProjectPaths | None, as_of_date: str) -> dict[str, Any]:
    paths = default_paths(paths)
    groups = []
    required = {"current_day_run", "data_refresh", "workflow", "daily_briefing", "portfolio_tracking"}
    for group, values in input_paths(paths, as_of_date).items():
        source = values["source"]
        audit = values.get("audit")
        audit_payload = load_json(audit) if audit else {}
        source_available = source.exists()
        audit_available = audit.exists() if audit else True
        groups.append(
            {
                "input_group": group,
                "required": group in required,
                "available": source_available and audit_available,
                "source_path": relative(source, paths.project_root),
                "source_audit_path": relative(audit, paths.project_root) if audit else None,
                "source_audit_passed": audit_payload.get("overall_passed") is True if audit and audit.exists() else None,
                "blocking_reasons": list(audit_payload.get("blocking_reasons", [])) if audit_payload else ([] if not group in required else ["input_missing"] if not source_available else []),
                "warnings": list(audit_payload.get("warnings", [])) if audit_payload else [],
            }
        )
    blocking = [
        f"{row['input_group']}_missing"
        for row in groups
        if row["required"] and not row["available"]
    ]
    return {
        "availability_id": "A-SHARE-OWNER-DASHBOARD-INPUT-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "input_groups": groups,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": sorted({warning for row in groups for warning in row.get("warnings", [])}),
    }
