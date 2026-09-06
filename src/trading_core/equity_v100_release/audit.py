"""Audit official v1.0.0 release artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_data_quality.common import BOUNDARY_FALSE
from trading_core.equity_v100_release.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, KNOWN_LIMITATIONS, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v100_release(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v100_release" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v100_release" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    decision = payloads["v100_final_release_decision"]
    prep = payloads["v100_prep_verification"]
    limitations = payloads["v100_known_limitations_register"]
    safety = payloads["v100_safety_boundary_statement"]
    blocking: list[str] = []
    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if len(JSON_NAMES) > 8:
        blocking.append("json_artifact_budget_exceeded")
    if len(markdowns) > 2:
        blocking.append("markdown_artifact_budget_exceeded")
    if decision.get("final_release_decision") != "released_as_research_only_simulation_platform":
        blocking.append("final_release_decision_not_released")
    if not decision.get("v100_prep_verified"):
        blocking.append("v100_prep_not_verified")
    if decision.get("release_readiness_decision_from_prep") != "ready_for_v100_release":
        blocking.append("prep_release_readiness_not_ready")
    if decision.get("full_regression_result") != "1807 passed, 1 skipped, 0 failed":
        blocking.append("full_regression_result_changed")
    if decision.get("blocking_warning_count") != 0:
        blocking.append("blocking_warning_count_not_zero")
    if decision.get("warnings") != []:
        blocking.append("final_release_warnings_not_empty")
    if limitations.get("known_limitations_count") != len(KNOWN_LIMITATIONS):
        blocking.append("known_limitations_count_mismatch")
    if not limitations.get("benchmark_warning_blocks_real_performance_claims"):
        blocking.append("benchmark_limitation_missing")
    if not safety.get("not_live_trading_ready"):
        blocking.append("not_live_trading_ready_missing")
    if prep.get("full_pytest_reused_from_v100_prep") is not True or prep.get("full_pytest_rerun") is not False:
        blocking.append("full_pytest_reuse_policy_violated")
    if decision.get("owner_readiness_state") != "blocked":
        blocking.append("owner_readiness_state_not_blocked")
    if decision.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_operationally_acceptable_not_false")
    if decision.get("source_readiness_score") != 54 or decision.get("minimum_owner_readiness_score") != 75 or decision.get("score_gap") != 21:
        blocking.append("owner_readiness_score_truth_changed")
    for key in BOUNDARY_FALSE:
        if decision.get(key) is True or prep.get(key) is True or safety.get(key) is True or limitations.get(key) is True:
            blocking.append(f"forbidden_boundary_true:{key}")
    audit = {
        "audit_id": "A-SHARE-V100-RELEASE-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
        "artifact_checks": {
            "json_count": len(JSON_NAMES),
            "markdown_count": len(MARKDOWN_NAMES),
            "all_json_present": all(bool(payload) for payload in payloads.values()),
            "all_markdown_present": all(path.exists() for path in markdowns),
            "json_artifact_budget_passed": len(JSON_NAMES) <= 8,
            "markdown_artifact_budget_passed": len(MARKDOWN_NAMES) <= 2,
        },
        "release_decision": {
            "final_release_decision": decision.get("final_release_decision"),
            "platform_scope": decision.get("platform_scope"),
            "v100_prep_verified": decision.get("v100_prep_verified"),
            "full_regression_result": decision.get("full_regression_result"),
            "blocking_warning_count": decision.get("blocking_warning_count"),
        },
        "owner_readiness": {
            "owner_readiness_state": decision.get("owner_readiness_state"),
            "owner_operationally_acceptable": decision.get("owner_operationally_acceptable"),
            "source_readiness_score": decision.get("source_readiness_score"),
            "minimum_owner_readiness_score": decision.get("minimum_owner_readiness_score"),
            "score_gap": decision.get("score_gap"),
        },
        "boundary": {key: decision.get(key) for key in BOUNDARY_FALSE},
        "known_limitations_count": limitations.get("known_limitations_count"),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v100_release_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V100_RELEASE_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v1.0.0 Release Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- final_release_decision: {audit['release_decision']['final_release_decision']}",
        f"- known_limitations_count: {audit['known_limitations_count']}",
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
