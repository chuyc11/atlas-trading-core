"""Fail-close audit for the v0.8.2 owner dashboard."""

from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import sha256_file, write_report
from trading_core.equity_owner_dashboard.dashboard_config import (
    DASHBOARD_FILES,
    DASHBOARD_REPORTS,
    DEFAULT_AS_OF_DATE,
    RECOMMENDED_NEXT_VERSION,
    REMEDIATION_VERSION,
    REQUIRED_CARDS,
    TARGET_VERSION,
    dashboard_artifact_paths,
)
from trading_core.equity_owner_dashboard.dashboard_report import render_audit
from trading_core.equity_owner_dashboard.dashboard_source_trace import forbidden_source_path_hits
from trading_core.storage.file_paths import ProjectPaths
from trading_core.system.common import default_paths


REQUIRED_ARTIFACTS = list(DASHBOARD_FILES) + list(DASHBOARD_REPORTS)


def audit_a_share_owner_dashboard(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = default_paths(paths)
    artifacts = dashboard_artifact_paths(paths, as_of_date)
    payloads = {key: _load_json(path) for key, path in artifacts.items() if key in DASHBOARD_FILES}
    checks = _checks(paths=paths, artifacts=artifacts, payloads=payloads)
    blocking = [f"{key}=false" for key, passed in checks.items() if not passed]
    warnings = sorted(
        set(payloads.get("warning_and_blocker_card", {}).get("warnings", []))
        | set(payloads.get("dashboard_input_availability", {}).get("warnings", []))
        | set(payloads.get("dashboard_boundary_check", {}).get("warnings", []))
    )
    audit = {
        "audit_id": "A-SHARE-OWNER-DASHBOARD-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "checks": checks,
        "card_checks": {
            "required_cards": {key: artifacts[key].exists() for key in REQUIRED_CARDS},
            "optional_cards": {
                key: artifacts[key].exists()
                for key in [
                    "provider_health_card",
                    "candidate_summary_card",
                    "portfolio_summary_card",
                    "benchmark_summary_card",
                    "performance_summary_card",
                    "attribution_summary_card",
                ]
            },
        },
        "boundary": payloads.get("dashboard_boundary_check", {}),
        "source_trace": {
            "source_trace_complete": payloads.get("dashboard_source_trace", {}).get("source_trace_complete"),
            "forbidden_path_hits": payloads.get("dashboard_source_trace", {}).get("forbidden_path_hits", []),
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION if not blocking else REMEDIATION_VERSION,
    }
    return write_report(artifacts["dashboard_audit_json"], audit, artifacts["dashboard_audit_report"], render_audit(audit))


def _checks(*, paths: ProjectPaths, artifacts: dict[str, Path], payloads: dict[str, Any]) -> dict[str, bool]:
    trace = payloads.get("dashboard_source_trace", {})
    boundary = payloads.get("dashboard_boundary_check", {})
    manifest = payloads.get("dashboard_manifest", {})
    summary = payloads.get("dashboard_summary", {})
    warning = payloads.get("warning_and_blocker_card", {})
    availability = payloads.get("dashboard_input_availability", {})
    return {
        "all_required_artifacts_exist": all(artifacts[key].exists() for key in REQUIRED_ARTIFACTS),
        "target_version_matches": all(payload.get("target_version") == TARGET_VERSION for payload in payloads.values() if payload),
        "input_availability_passed": availability.get("overall_passed") is True,
        "required_cards_present": all(artifacts[key].exists() and bool(payloads.get(key)) for key in REQUIRED_CARDS),
        "optional_cards_present": all(
            artifacts[key].exists()
            for key in [
                "provider_health_card",
                "candidate_summary_card",
                "portfolio_summary_card",
                "benchmark_summary_card",
                "performance_summary_card",
                "attribution_summary_card",
            ]
        ),
        "warning_blocker_card_passed": warning.get("overall_passed") is True,
        "no_blocking_reasons": not warning.get("blocking_reasons"),
        "source_trace_complete": trace.get("source_trace_complete") is True,
        "source_trace_no_forbidden_paths": not forbidden_source_path_hits(trace.get("source_artifacts", []) + trace.get("output_artifacts", [])),
        "source_trace_hashes_match": _source_hashes_match(paths, trace),
        "boundary_overall_passed": boundary.get("overall_passed") is True,
        "no_forbidden_artifacts_generated": not boundary.get("forbidden_artifacts_present"),
        "no_forbidden_positive_wording": not boundary.get("forbidden_wording_positive_hits"),
        "manifest_generated": manifest.get("manifest_id") == "A-SHARE-OWNER-DASHBOARD-MANIFEST",
        "manifest_boundary_passed": manifest.get("boundary", {}).get("overall_passed") is True,
        "summary_generated": summary.get("summary_id") == "A-SHARE-OWNER-DASHBOARD-SUMMARY",
        "compact_report_exists": artifacts["owner_dashboard_compact_report"].exists(),
        "full_report_exists": artifacts["owner_dashboard_report"].exists(),
    }


def _source_hashes_match(paths: ProjectPaths, trace: dict[str, Any]) -> bool:
    for row in trace.get("source_artifacts", []):
        path = Path(row.get("path", ""))
        if not path.is_absolute():
            path = paths.project_root / path
        if path.exists() and row.get("sha256") and sha256_file(path) != row.get("sha256"):
            return False
    return True


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except JSONDecodeError:
        return {}
    return value if isinstance(value, dict) else {}
