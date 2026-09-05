"""Manifest helpers for A-share daily research workflow orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file
from trading_core.equity_workflows.workflow_config import (
    INPUT_VERSIONS,
    RECOMMENDED_NEXT_VERSION,
    TARGET_VERSION,
    WORKFLOW_BOUNDARY,
    WORKFLOW_FLAGS,
    upstream_audit_artifacts,
)
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import relative


def build_stage_manifest(*, as_of_date: str, mode: str, stages: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DAILY-RESEARCH-WORKFLOW-STAGE-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "generated_at": generated_at,
        "stages": stages,
        "stage_count": len(stages),
        **WORKFLOW_FLAGS,
        "boundary": dict(WORKFLOW_BOUNDARY),
    }


def build_run_manifest(
    *,
    as_of_date: str,
    mode: str,
    started_at: str,
    finished_at: str,
    duration_seconds: float,
    stages: list[dict[str, Any]],
    warnings: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-DAILY-RESEARCH-WORKFLOW-RUN-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "overall_passed": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
        "warnings": warnings,
        "stages": stages,
        "input_versions": dict(INPUT_VERSIONS),
        "build_timestamp_non_strict_idempotency": True,
        **WORKFLOW_FLAGS,
        **WORKFLOW_BOUNDARY,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def build_boundary_check(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    warnings: list[str],
    blocking_reasons: list[str],
) -> dict[str, Any]:
    forbidden = forbidden_artifacts(paths, as_of_date)
    blocking = list(blocking_reasons)
    if forbidden:
        blocking.append("forbidden_artifacts_present")
    return {
        "boundary_id": "A-SHARE-DAILY-WORKFLOW-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        **WORKFLOW_BOUNDARY,
        "forbidden_artifacts_present": forbidden,
        "forbidden_wording_positive_hits": [],
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        **WORKFLOW_FLAGS,
    }


def build_workflow_summary(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    mode: str,
    run_manifest: dict[str, Any],
    source_trace: dict[str, Any],
    boundary_check: dict[str, Any],
) -> dict[str, Any]:
    counts = _candidate_counts(paths, as_of_date)
    navs = _portfolio_navs(paths, as_of_date)
    return {
        "summary_id": "A-SHARE-DAILY-RESEARCH-WORKFLOW-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "mode": mode,
        "overall_passed": bool(run_manifest.get("overall_passed")) and bool(boundary_check.get("overall_passed")),
        "blocking_reasons": list(run_manifest.get("blocking_reasons", [])) + list(boundary_check.get("blocking_reasons", [])),
        "warnings": sorted({*run_manifest.get("warnings", []), *boundary_check.get("warnings", [])}),
        "stage_counts": stage_counts(run_manifest.get("stages", [])),
        "required_stage_status": {stage["stage_id"]: stage["status"] for stage in run_manifest.get("stages", [])},
        "candidate_counts": counts,
        "portfolio_navs": navs,
        "briefing_path": relative(paths.data_dir / "equity_briefings" / "daily" / as_of_date / "briefing_manifest.json", paths.project_root),
        "tracking_path": relative(paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "tracking_manifest.json", paths.project_root),
        "source_trace_complete": bool(source_trace.get("source_trace_complete")),
        "upstream_audits_passed": upstream_audits_passed(paths),
        "build_timestamp_non_strict_idempotency": True,
        **WORKFLOW_FLAGS,
        "boundary": dict(WORKFLOW_BOUNDARY),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def stage_counts(stages: list[dict[str, Any]]) -> dict[str, int]:
    statuses = {"passed": 0, "failed": 0, "skipped": 0, "blocked": 0, "not_run": 0}
    for stage in stages:
        status = str(stage.get("status") or "not_run")
        statuses[status] = statuses.get(status, 0) + 1
    return {"total": len(stages), **statuses}


def upstream_audits_passed(paths: ProjectPaths) -> bool:
    return all(_load_json(path).get("overall_passed") is True for path in upstream_audit_artifacts(paths).values())


def forbidden_artifacts(paths: ProjectPaths, as_of_date: str) -> list[str]:
    candidates = [
        paths.data_dir / "equity_workflows" / "daily" / as_of_date / "ORDER_PREVIEW.md",
        paths.data_dir / "equity_workflows" / "daily" / as_of_date / "BROKER_ORDER.json",
        paths.data_dir / "equity_workflows" / "daily" / as_of_date / "REAL_ORDER.json",
        paths.outputs_dir / "equity_workflows" / "daily" / as_of_date / "ORDER_PREVIEW.md",
        paths.outputs_dir / "equity_workflows" / "daily" / as_of_date / "BUY_LIST.md",
        paths.outputs_dir / "equity_workflows" / "daily" / as_of_date / "SELL_LIST.md",
        paths.outputs_dir / "orders" / f"ORDER_PREVIEW-{as_of_date}.md",
        paths.data_dir / "orders" / f"orders-{as_of_date}.jsonl",
        paths.data_dir / "trades" / f"trades-{as_of_date}.jsonl",
        paths.data_dir / "accounts" / f"account-{as_of_date}.json",
    ]
    return [relative(path, paths.project_root) for path in candidates if path.exists()]


def artifact_record(paths: ProjectPaths, path: Path) -> dict[str, Any]:
    return {
        "path": relative(path, paths.project_root),
        "exists": path.exists(),
        "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
    }


def load_json(path: Path) -> dict[str, Any]:
    return _load_json(path)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _candidate_counts(paths: ProjectPaths, as_of_date: str) -> dict[str, int]:
    base = paths.data_dir / "equity_selection" / "daily" / as_of_date
    keys = {
        "long": base / "long_candidates.json",
        "mid": base / "mid_candidates.json",
        "short": base / "short_candidates.json",
        "extended": base / "extended_watch_pool.json",
    }
    result = {}
    for key, path in keys.items():
        if not path.exists():
            result[key] = 0
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        result[key] = len(value) if isinstance(value, list) else 0
    return result


def _portfolio_navs(paths: ProjectPaths, as_of_date: str) -> dict[str, float | None]:
    path = paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "portfolio_nav_snapshot.json"
    payload = _load_json(path)
    portfolios = payload.get("portfolios", {})
    return {
        key: (float(record.get("portfolio_nav")) if isinstance(record, dict) and record.get("portfolio_nav") is not None else None)
        for key, record in portfolios.items()
    }
