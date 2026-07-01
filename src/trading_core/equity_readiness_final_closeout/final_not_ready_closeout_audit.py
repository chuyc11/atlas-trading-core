"""Audit v0.9.6 final not-ready closeout artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_readiness_final_closeout.builder import DEFAULT_AS_OF_DATE, RECOMMENDED_NEXT_VERSION, SOURCE_READINESS_SCORE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_final_not_ready_closeout(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = paths.data_dir / "equity_readiness_final_closeout" / "daily" / as_of_date
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_final_not_ready_closeout_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_FINAL_NOT_READY_CLOSEOUT_AUDIT.md"

    source = read_json(data_dir / "source_evidence_review.json")
    branch = read_json(data_dir / "branch_selection_result.json")
    disallowance = read_json(data_dir / "controlled_reevaluation_disallowance_record.json")
    result = read_json(data_dir / "final_not_ready_closeout_result.json")
    requirements = read_json(data_dir / "additional_evidence_requirement_register.json")
    next_plan = read_json(data_dir / "next_cycle_evidence_plan.json")
    blocker_summary = read_json(data_dir / "unresolved_blocker_closeout_summary.json")
    owner_summary = read_json(data_dir / "owner_not_ready_summary.json")
    backlog = read_json(data_dir / "developer_follow_up_backlog.json")
    boundary = read_json(data_dir / "final_closeout_boundary_check.json")
    manifest = read_json(data_dir / "final_closeout_manifest.json")

    markdown_paths = [
        paths.outputs_dir / "equity_readiness_final_closeout" / "daily" / as_of_date / "A_SHARE_FINAL_NOT_READY_CLOSEOUT.md",
        paths.outputs_dir / "equity_readiness_final_closeout" / "daily" / as_of_date / "A_SHARE_ADDITIONAL_EVIDENCE_REQUIREMENT_PLAN.md",
        paths.outputs_dir / "equity_readiness_final_closeout" / "daily" / as_of_date / "A_SHARE_OWNER_NOT_READY_SUMMARY.md",
    ]
    source_checks = {
        "v095_baseline_verified": bool(source.get("review_passed")),
        "v095_future_reevaluation_decision": source.get("future_reevaluation_decision"),
        "v095_ready_for_future_controlled_reevaluation_prep": bool(source.get("ready_for_future_controlled_reevaluation_prep")),
        "source_readiness_score": source.get("source_readiness_score"),
        "owner_readiness_state": source.get("owner_readiness_state"),
    }
    branch_checks = {
        "selected_branch": branch.get("selected_branch"),
        "controlled_reevaluation_allowed": bool(branch.get("controlled_reevaluation_allowed")),
        "controlled_reevaluation_executed": bool(branch.get("controlled_reevaluation_executed")),
    }
    closeout_checks = {
        "source_evidence_review_generated": bool(source),
        "branch_selection_result_generated": bool(branch),
        "controlled_reevaluation_disallowance_record_generated": bool(disallowance),
        "final_not_ready_closeout_result_generated": bool(result),
        "additional_evidence_requirement_register_generated": bool(requirements),
        "next_cycle_evidence_plan_generated": bool(next_plan),
        "unresolved_blocker_closeout_summary_generated": bool(blocker_summary),
        "owner_not_ready_summary_generated": bool(owner_summary),
        "developer_follow_up_backlog_generated": bool(backlog),
        "boundary_check_generated": bool(boundary),
        "manifest_generated": bool(manifest),
        "markdown_reports_generated": all(path.exists() for path in markdown_paths),
    }
    boundary_checks = {
        "data_refresh_run": bool(boundary.get("data_refresh_run")),
        "research_pipeline_rerun_run": bool(boundary.get("research_pipeline_rerun_run")),
        "build_from_existing_data_run": bool(boundary.get("build_from_existing_data_run")),
        "owner_readiness_gate_rerun": bool(boundary.get("owner_readiness_gate_rerun")),
        "controlled_gate_reevaluation_run": bool(boundary.get("controlled_gate_reevaluation_run")),
        "new_gate_score_generated": bool(boundary.get("new_gate_score_generated")),
        "new_gate_decision_generated": bool(boundary.get("new_gate_decision_generated")),
        "threshold_lowered": bool(boundary.get("threshold_lowered")),
        "auto_waiver_allowed": bool(boundary.get("auto_waiver_allowed")),
        "manual_waiver_approval_recorded": bool(boundary.get("manual_waiver_approval_recorded")),
        "broker_connected": bool(boundary.get("broker_connected")),
        "real_account_data_read": bool(boundary.get("real_account_data_read")),
        "real_orders_placed": bool(boundary.get("real_orders_placed")),
        "order_preview_generated": bool(boundary.get("order_preview_generated")),
        "buy_sell_signals_generated": bool(boundary.get("buy_sell_signals_generated")),
        "old_run_daily_called": bool(boundary.get("old_run_daily_called")),
        "day2_executed": bool(boundary.get("day2_executed")),
        "live_trading_ready": bool(boundary.get("live_trading_ready")),
    }
    text_checks = {
        "final_closeout_not_labeled_as_gate_decision": result.get("final_closeout_decision") == "not_ready_additional_evidence_required",
        "owner_summary_not_labeled_as_investment_advice": bool(owner_summary.get("not_investment_advice")),
        "owner_summary_not_order_instruction": bool(owner_summary.get("not_order_instruction")),
        "protected_paths_untouched": bool(boundary.get("protected_paths_untouched")),
    }

    blocking = []
    if not source_checks["v095_baseline_verified"]:
        blocking.append("v095_baseline_not_verified")
    if source_checks["v095_future_reevaluation_decision"] != "no_go_additional_evidence_required":
        blocking.append("unexpected_v095_future_reevaluation_decision")
    if source_checks["v095_ready_for_future_controlled_reevaluation_prep"] is not False:
        blocking.append("v095_ready_flag_not_false")
    if branch_checks["selected_branch"] != "final_not_ready_closeout":
        blocking.append("selected_branch_not_final_not_ready_closeout")
    if branch_checks["controlled_reevaluation_allowed"] is not False or branch_checks["controlled_reevaluation_executed"] is not False:
        blocking.append("controlled_reevaluation_not_disallowed")
    blocking.extend(key for key, value in closeout_checks.items() if not value)
    blocking.extend(key for key, value in boundary_checks.items() if value)
    blocking.extend(key for key, value in text_checks.items() if not value)
    blocking.extend(result.get("blocking_reasons", []))
    blocking.extend(boundary.get("blocking_reasons", []))

    audit = {
        "audit_id": "A-SHARE-FINAL-NOT-READY-CLOSEOUT-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [*result.get("warnings", []), *boundary.get("warnings", [])],
        "source_checks": source_checks,
        "branch_checks": branch_checks,
        "closeout_checks": closeout_checks,
        "boundary": boundary_checks,
        "text_checks": text_checks,
        "test_policy": {
            "targeted_pytest_required": True,
            "full_pytest_run": False,
            "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "audit_json_path": _rel(audit_path, paths.project_root),
        "audit_markdown_path": _rel(report_path, paths.project_root),
    }
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share Final Not-Ready Closeout Audit",
        "",
        "## Summary",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        "",
        "## Source Checks",
        *[f"- {key}: {value}" for key, value in audit["source_checks"].items()],
        "",
        "## Branch Checks",
        *[f"- {key}: {value}" for key, value in audit["branch_checks"].items()],
        "",
        "## Closeout Checks",
        *[f"- {key}: {value}" for key, value in audit["closeout_checks"].items()],
        "",
        "## Boundary",
        *[f"- {key}: {value}" for key, value in audit["boundary"].items()],
        "",
        "## Test Policy",
        "- full_pytest_run: false",
        "",
        "## Recommended Next Version",
        f"- {audit['recommended_next_version']}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
