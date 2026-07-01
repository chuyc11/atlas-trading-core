"""Audit v1.0.0-prep closeout artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE
from trading_core.equity_v100_prep.builder import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, TARGET_VERSION, V100_JSON_NAMES, V100_MARKDOWN_NAMES
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v100_prep(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v100_prep" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v100_prep" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in V100_JSON_NAMES}
    markdowns = [output_dir / name for name in V100_MARKDOWN_NAMES]
    decision = payloads["v100_release_readiness_decision"]
    warning = payloads["v098_warning_classification"]
    regression = payloads["v100_full_regression_result"]
    cli = payloads["v100_cli_surface_verification"]
    integrity = payloads["v100_artifact_integrity_check"]
    boundary = payloads["v100_safety_boundary_sweep"]

    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if decision.get("release_readiness_decision") != "ready_for_v100_release":
        blocking.append("release_readiness_decision_not_ready")
    if not decision.get("v098_platform_verified"):
        blocking.append("v098_platform_not_verified")
    if warning.get("blocking_warning_count") != 0:
        blocking.append("blocking_warnings_present")
    if not regression.get("full_regression_passed"):
        blocking.append("full_regression_not_passed")
    if not cli.get("cli_surface_verified"):
        blocking.append("cli_surface_not_verified")
    if not integrity.get("artifact_integrity_passed"):
        blocking.append("artifact_integrity_not_passed")
    if not boundary.get("safety_boundary_sweep_passed"):
        blocking.append("safety_boundary_sweep_not_passed")
    if decision.get("owner_readiness_state") != "blocked":
        blocking.append("owner_readiness_state_not_blocked")
    if decision.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_operationally_acceptable_not_false")
    if decision.get("source_readiness_score") != 54 or decision.get("minimum_owner_readiness_score") != 75 or decision.get("score_gap") != 21:
        blocking.append("owner_readiness_score_truth_changed")
    for key in BOUNDARY_FALSE:
        if decision.get(key) is True or boundary.get(key) is True:
            blocking.append(f"forbidden_boundary_true:{key}")

    warnings = warning.get("classifications", [])
    audit = {
        "audit_id": "A-SHARE-V100-PREP-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": warnings,
        "artifact_checks": {
            "json_count": len(V100_JSON_NAMES),
            "markdown_count": len(V100_MARKDOWN_NAMES),
            "all_json_present": all(bool(payload) for payload in payloads.values()),
            "all_markdown_present": all(path.exists() for path in markdowns),
        },
        "readiness_decision": {
            "release_readiness_decision": decision.get("release_readiness_decision"),
            "v098_platform_verified": decision.get("v098_platform_verified"),
            "blocking_warning_count": decision.get("blocking_warning_count"),
            "full_regression_passed": decision.get("full_regression_passed"),
            "cli_surface_verified": decision.get("cli_surface_verified"),
            "artifact_integrity_passed": decision.get("artifact_integrity_passed"),
            "safety_boundary_sweep_passed": decision.get("safety_boundary_sweep_passed"),
        },
        "owner_readiness": {
            "owner_readiness_state": decision.get("owner_readiness_state"),
            "owner_operationally_acceptable": decision.get("owner_operationally_acceptable"),
            "source_readiness_score": decision.get("source_readiness_score"),
            "minimum_owner_readiness_score": decision.get("minimum_owner_readiness_score"),
            "score_gap": decision.get("score_gap"),
        },
        "boundary": {key: boundary.get(key) for key in BOUNDARY_FALSE},
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v100_prep_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V100_PREP_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.0.0-prep Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- release_readiness_decision: {audit['readiness_decision']['release_readiness_decision']}",
        "",
        "## Owner Readiness",
        *[f"- {key}: {value}" for key, value in audit["owner_readiness"].items()],
        "",
        "## Boundary",
        *[f"- {key}: {value}" for key, value in audit["boundary"].items()],
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
