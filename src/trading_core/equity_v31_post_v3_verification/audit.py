"""Audit v3.1.0 post-v3 verification artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_v09_platform.builder import BOUNDARY_FALSE, BOUNDARY_TRUE
from trading_core.equity_v31_post_v3_verification.builder import DEFAULT_AS_OF_DATE, JSON_NAMES, MARKDOWN_NAMES, RECOMMENDED_NEXT_VERSION, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_v31_post_v3_verification(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_v31_post_v3_verification" / "daily" / as_of_date
    output_dir = paths.outputs_dir / "equity_v31_post_v3_verification" / "daily" / as_of_date
    payloads = {name: read_json(data_dir / f"{name}.json") for name in JSON_NAMES}
    result = payloads["v31_post_v3_verification_result"]
    markdowns = [output_dir / name for name in MARKDOWN_NAMES]
    blocking: list[str] = []

    blocking.extend(name for name, payload in payloads.items() if not payload)
    if not all(path.exists() for path in markdowns):
        blocking.append("required_markdown_reports_missing")
    if result.get("target_version") != TARGET_VERSION:
        blocking.append("target_version_mismatch")
    if result.get("overall_passed") is not True:
        blocking.append("result_not_passed")
    if result.get("blocking_reasons") != []:
        blocking.append("result_blocking_reasons_not_empty")
    for key in _required_true_fields():
        if result.get(key) is not True:
            blocking.append(f"required_true_missing:{key}")
    for key in _required_false_fields():
        if result.get(key) is not False:
            blocking.append(f"required_false_not_false:{key}")
    for key, expected in BOUNDARY_TRUE.items():
        if result.get(key) is not expected:
            blocking.append(f"boundary_true_missing:{key}")
    for key in BOUNDARY_FALSE:
        if result.get(key) is not False:
            blocking.append(f"forbidden_boundary_true:{key}")
    if result.get("full_regression_total_passed") != 2024 or result.get("full_regression_total_skipped") != 1:
        blocking.append("full_regression_totals_mismatch")
    if result.get("full_regression_mode") != "split_matrix":
        blocking.append("full_regression_mode_not_split_matrix")
    if result.get("owner_readiness_state") != "blocked" or result.get("owner_operationally_acceptable") is not False:
        blocking.append("owner_state_mismatch")

    audit = {
        "audit_id": "A-SHARE-V31-POST-V3-VERIFICATION-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": result.get("warnings", []),
        "artifact_checks": {
            "json_count": len(JSON_NAMES),
            "markdown_count": len(MARKDOWN_NAMES),
            "audit_markdown_count": 1,
            "all_json_present": all(bool(payload) for payload in payloads.values()),
            "all_markdown_present": all(path.exists() for path in markdowns),
            "json_budget_passed": len(JSON_NAMES) <= 26,
            "markdown_budget_passed": len(MARKDOWN_NAMES) <= 11,
            "audit_markdown_budget_passed": True,
        },
        "quality_checks": {key: result.get(key) for key in _required_true_fields()},
        "forbidden_checks": {key: result.get(key) for key in _required_false_fields()},
        "owner_readiness_state": result.get("owner_readiness_state"),
        "owner_operationally_acceptable": result.get("owner_operationally_acceptable"),
        "live_trading_ready": result.get("live_trading_ready"),
        "full_regression_mode": result.get("full_regression_mode"),
        "full_regression_total_passed": result.get("full_regression_total_passed"),
        "full_regression_total_skipped": result.get("full_regression_total_skipped"),
        "release_readiness_decision": "passed" if not blocking else "blocked",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_v31_post_v3_verification_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_V31_POST_V3_VERIFICATION_AUDIT.md"
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _required_true_fields() -> list[str]:
    return [
        "v30_baseline_verified",
        "semantic_fix_commit_verified",
        "semantic_regression_pack_generated",
        "split_matrix_regression_evidence_generated",
        "test_evidence_truthfulness_contract_generated",
        "git_diff_evidence_pack_generated",
        "artifact_checksum_provenance_pack_generated",
        "external_reviewer_audit_package_generated",
        "local_environment_limitation_result_generated",
        "owner_post_v3_verification_dashboard_generated",
        "not_live_trading_ready_explanation_generated",
        "t_plus_one_dated_settlement_verified",
        "same_day_sell_rejection_verified",
        "holiday_settlement_delay_verified",
        "period_cumulative_excess_return_verified",
        "formal_calendar_fail_closed_verified",
        "raw_adjusted_price_fallback_blocked_by_default",
        "execution_path_market_constraints_verified",
        "account_apply_trade_bypass_absent",
        "full_regression_run",
        "full_regression_passed",
        "single_command_pytest_blocked_by_local_timeout_or_windows_limit",
        "artifact_integrity_sweep_passed",
        "protected_path_sweep_passed",
        "safety_boundary_sweep_passed",
    ]


def _required_false_fields() -> list[str]:
    return [
        "single_command_pytest_completed",
        "fabricated_test_result",
        "fabricated_split_matrix_result",
        "fabricated_audit_evidence",
        "fabricated_checksum",
        "fabricated_git_evidence",
        "fabricated_semantic_fix_evidence",
        "historical_evidence_deleted",
        "audit_evidence_deleted",
        "release_evidence_deleted",
        "required_artifacts_deleted",
        "owner_operationally_acceptable",
        "owner_readiness_gate_rerun",
        "controlled_gate_reevaluation_run",
        "new_gate_score_generated",
        "new_gate_decision_generated",
        "broker_connected",
        "real_account_data_read",
        "real_orders_placed",
        "real_order_preview_generated",
        "buy_sell_signals_generated",
        "old_run_daily_called",
        "day2_executed",
        "live_trading_ready",
    ]


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share v3.1 Post-v3 Verification Audit",
        "",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- full_regression_mode: {audit['full_regression_mode']}",
        f"- full_regression_total_passed: {audit['full_regression_total_passed']}",
        f"- full_regression_total_skipped: {audit['full_regression_total_skipped']}",
        f"- owner_readiness_state: {audit['owner_readiness_state']}",
        f"- live_trading_ready: {audit['live_trading_ready']}",
        "",
        "## Artifact Checks",
        *[f"- {key}: {value}" for key, value in audit["artifact_checks"].items()],
        "",
        "## Quality Checks",
        *[f"- {key}: {value}" for key, value in audit["quality_checks"].items()],
        "",
        "## Forbidden Checks",
        *[f"- {key}: {value}" for key, value in audit["forbidden_checks"].items()],
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
