"""Build a current daily workflow readiness snapshot for v0.6.2."""

from __future__ import annotations

from typing import Any

from trading_core.execution.common import read_dict
from trading_core.forward_dry_run.start_authorization_common import (
    AS_OF_DATE,
    AUTHORIZATION_NOTICE,
    authorization_boundary,
    non_claim_markdown,
    paths_or_default,
    system_json,
    system_report,
    write_artifact,
)
from trading_core.storage.file_paths import ProjectPaths


def build_current_daily_workflow_readiness_snapshot(*, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths_or_default(paths)
    audit = read_dict(paths.data_dir / "system" / "daily_workflow_audit.json")
    snapshot = read_dict(paths.data_dir / "daily_workflow" / "snapshots" / f"daily_market_data_snapshot-{AS_OF_DATE}.json")
    payload: dict[str, Any] = {
        "snapshot_id": "CURRENT-DAILY-WORKFLOW-READINESS-SNAPSHOT",
        "daily_workflow_audit_passed": audit.get("overall_passed") is True and not audit.get("blocking_reasons"),
        "historical_daily_workflow_fixture_as_of_date": AS_OF_DATE,
        "latest_available_trading_date_from_local_data": snapshot.get("latest_available_trading_date"),
        "historical_daily_workflow_fixture_passed": audit.get("overall_passed") is True and not audit.get("blocking_reasons"),
        "current_production_daily_workflow_authorized": False,
        "real_time_market_data_downloaded": False,
        "external_api_called": False,
        "boundary": authorization_boundary("snapshot_only"),
    }
    return write_artifact(
        system_json(paths, "current_daily_workflow_readiness_snapshot.json"),
        payload,
        system_report(paths, "CURRENT_DAILY_WORKFLOW_READINESS_SNAPSHOT.md"),
        build_markdown(payload),
    )


def build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Current Daily Workflow Readiness Snapshot",
        "",
        AUTHORIZATION_NOTICE,
        "",
        "## Summary",
        f"- daily_workflow_audit_passed: {str(payload['daily_workflow_audit_passed']).lower()}",
        f"- historical_daily_workflow_fixture_as_of_date: {payload['historical_daily_workflow_fixture_as_of_date']}",
        f"- latest_available_trading_date_from_local_data: {payload['latest_available_trading_date_from_local_data']}",
        "- historical_daily_workflow_fixture_passed: true",
        "- current_production_daily_workflow_authorized: false",
        "",
        "## Boundary",
        *non_claim_markdown(),
        "",
    ]
    return "\n".join(lines)

