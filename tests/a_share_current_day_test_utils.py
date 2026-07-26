from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_refresh.data_refresh_config import data_refresh_artifact_paths
from trading_core.storage.file_paths import ProjectPaths


AS_OF_DATE = "2026-06-26"


def make_paths(tmp_path: Path) -> ProjectPaths:
    root = tmp_path / "workspace"
    project = root / "work" / "trading-core"
    project.mkdir(parents=True)
    return ProjectPaths(root)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def seed_data_refresh(paths: ProjectPaths, *, passed: bool = True, as_of_date: str = AS_OF_DATE) -> None:
    artifacts = data_refresh_artifact_paths(paths, as_of_date)
    warnings = ["daily_basic:required_field_all_null", "trading_calendar:exchange_level_calendar_collapsed_to_trade_date"]
    audit = {
        "audit_id": "A-SHARE-DAILY-DATA-REFRESH-AUDIT",
        "target_version": "v0.8.0-a-share-daily-data-refresh-and-provider-hardening",
        "as_of_date": as_of_date,
        "mode": "validate_existing_data",
        "overall_passed": passed,
        "blocking_reasons": [] if passed else ["freshness_validation_passed=false"],
        "warnings": warnings,
        "dataset_checks": {
            "equity_master": "passed",
            "daily_price": "passed",
            "adjusted_price": "passed",
            "daily_basic": "passed",
            "index_price": "passed",
            "industry_classification": "passed",
            "financial_indicators": "passed",
            "trading_calendar": "passed",
        },
        "validation_checks": {
            "schema_validation_passed": passed,
            "freshness_validation_passed": passed,
            "coverage_validation_passed": passed,
            "critical_datasets_available": passed,
        },
        "recommended_next_version": "v0.8.1-a-share-current-day-research-workflow-runner",
    }
    for _key, path in artifacts.items():
        if path.suffix == ".json":
            write_json(path, {"target_version": audit["target_version"], "as_of_date": as_of_date})
    write_json(artifacts["date_resolution"], {"target_version": audit["target_version"], "as_of_date": as_of_date, "resolved_as_of_date": as_of_date})
    write_json(artifacts["data_refresh_audit_json"], audit)


def fake_workflow_audit(as_of_date: str = AS_OF_DATE) -> dict[str, Any]:
    return {
        "audit_id": "A-SHARE-DAILY-WORKFLOW-AUDIT",
        "target_version": "v0.7.9-a-share-daily-workflow-orchestration",
        "as_of_date": as_of_date,
        "mode": "validate_existing_artifacts",
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": ["workflow informational warning"],
        "stage_counts": {"total": 11, "passed": 11},
        "recommended_next_version": "v0.7.10-a-share-benchmark-data-and-performance-comparison",
    }
