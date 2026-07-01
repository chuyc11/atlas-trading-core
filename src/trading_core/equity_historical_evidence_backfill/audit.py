"""Audit v0.9.7 historical evidence backfill and refresh planning artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_historical_evidence_backfill.builder import DEFAULT_AS_OF_DATE, TARGET_VERSION
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_historical_evidence_backfill_and_refresh_plan(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    historical_dir = paths.data_dir / "equity_historical_research_backfill" / "daily" / as_of_date
    evidence_dir = paths.data_dir / "equity_research_evidence_recomputed" / "daily" / as_of_date
    closeout_dir = paths.data_dir / "equity_reevaluation_readiness_closeout" / "daily" / as_of_date
    refresh_dir = paths.data_dir / "equity_post_close_refresh_planning" / "daily" / as_of_date
    audit_path = paths.data_dir / "equity_data_quality" / "a_share_historical_backfill_and_refresh_planning_audit.json"
    report_path = paths.outputs_dir / "audit" / "A_SHARE_HISTORICAL_BACKFILL_AND_REFRESH_PLANNING_AUDIT.md"

    discovery = read_json(historical_dir / "historical_trading_day_discovery.json")
    availability = read_json(historical_dir / "historical_source_data_availability.json")
    backfill = read_json(historical_dir / "historical_research_backfill_result.json")
    historical_boundary = read_json(historical_dir / "historical_backfill_boundary_check.json")
    recomputed = read_json(evidence_dir / "recomputed_evidence_result.json")
    register = read_json(evidence_dir / "recomputed_evidence_eligible_day_register.json")
    precheck = read_json(closeout_dir / "reevaluation_readiness_precheck.json")
    go_no_go = read_json(closeout_dir / "go_no_go_after_backfill.json")
    closeout = read_json(closeout_dir / "reevaluation_readiness_closeout_result.json")
    readiness_boundary = read_json(closeout_dir / "reevaluation_readiness_boundary_check.json")
    refresh_plan = read_json(refresh_dir / "post_close_refresh_plan.json")
    command_plan = read_json(refresh_dir / "post_close_refresh_command_plan.json")
    refresh_boundary = read_json(refresh_dir / "post_close_refresh_safety_boundary.json")
    schedule = read_json(refresh_dir / "post_close_refresh_schedule_recommendation.json")
    v096_audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_final_not_ready_closeout_audit.json")

    artifact_checks = {
        "v096_baseline_verified": bool(v096_audit.get("overall_passed")),
        "historical_trading_day_discovery_generated": bool(discovery),
        "historical_source_data_availability_assessed": bool(availability),
        "historical_backfill_result_generated": bool(backfill),
        "recomputed_evidence_result_generated": bool(recomputed),
        "go_no_go_after_backfill_generated": bool(go_no_go),
        "post_close_refresh_plan_generated": bool(refresh_plan),
        "lookback_before_2026_06_26_executed": bool(discovery.get("lookback_before_2026_06_26_executed")),
        "existing_eligible_days_reused": set(backfill.get("reused_existing_days", [])) == {"2026-06-26", "2026-07-01"},
        "backfill_days_from_trading_days_only": set(backfill.get("selected_backfill_days", [])).issubset(set(discovery.get("resolved_trading_days", []))),
        "target_evidence_count_not_fabricated": bool(backfill.get("target_count_not_fabricated")) and bool(register.get("target_count_not_fabricated")),
    }
    boundary_checks = {
        "owner_readiness_gate_rerun": bool(readiness_boundary.get("owner_readiness_gate_rerun") or historical_boundary.get("owner_readiness_gate_rerun")),
        "controlled_reevaluation_executed": bool(readiness_boundary.get("controlled_reevaluation_executed") or historical_boundary.get("controlled_reevaluation_executed")),
        "new_gate_score_generated": bool(readiness_boundary.get("new_gate_score_generated") or historical_boundary.get("new_gate_score_generated")),
        "new_gate_decision_generated": bool(readiness_boundary.get("new_gate_decision_generated") or historical_boundary.get("new_gate_decision_generated")),
        "threshold_lowered": bool(readiness_boundary.get("threshold_lowered") or historical_boundary.get("threshold_lowered")),
        "waiver_applied": bool(readiness_boundary.get("auto_waiver_allowed") or readiness_boundary.get("manual_waiver_approval_recorded")),
        "broker_connected": bool(readiness_boundary.get("broker_connected") or refresh_boundary.get("broker_connected")),
        "real_account_data_read": bool(readiness_boundary.get("real_account_data_read") or refresh_boundary.get("real_account_data_read")),
        "real_orders_placed": bool(readiness_boundary.get("real_orders_placed") or refresh_boundary.get("real_orders_placed")),
        "order_preview_generated": bool(readiness_boundary.get("order_preview_generated") or refresh_boundary.get("order_preview_generated")),
        "buy_sell_signals_generated": bool(readiness_boundary.get("buy_sell_signals_generated") or refresh_boundary.get("buy_sell_signals_generated")),
        "old_run_daily_called": bool(readiness_boundary.get("old_run_daily_called")),
        "day2_executed": bool(readiness_boundary.get("day2_executed")),
        "live_trading_ready": bool(readiness_boundary.get("live_trading_ready") or refresh_boundary.get("live_trading_ready")),
        "protected_paths_untouched": bool(readiness_boundary.get("protected_paths_untouched") and historical_boundary.get("protected_paths_untouched")),
    }
    refresh_checks = {
        "post_close_plan_public_data_only": bool(refresh_plan.get("public_market_data_only")),
        "post_close_plan_excludes_broker_orders_signals_gate": {"broker", "real_account", "orders", "order_preview", "buy_sell_signals", "owner_readiness_gate", "controlled_reevaluation"}.issubset(set(refresh_plan.get("explicitly_excluded_scope", []))),
        "post_close_plan_does_not_install_scheduler": schedule.get("installs_scheduler") is False and refresh_boundary.get("installs_scheduler") is False,
        "post_close_plan_recommended_time": refresh_plan.get("recommended_run_time") == "15:45",
        "post_close_plan_timezone": refresh_plan.get("timezone") == "Asia/Shanghai",
    }
    readiness_checks = {
        "known_owner_readiness_state": recomputed.get("known_owner_readiness_state"),
        "owner_operationally_acceptable": bool(recomputed.get("owner_operationally_acceptable")),
        "source_readiness_score": recomputed.get("source_readiness_score"),
        "minimum_owner_readiness_score": recomputed.get("minimum_owner_readiness_score"),
        "score_gap": recomputed.get("score_gap"),
        "not_owner_readiness_gate_decision": bool(go_no_go.get("not_owner_readiness_gate_decision")),
    }

    blocking = []
    blocking.extend(key for key, value in artifact_checks.items() if not value)
    blocking.extend(key for key, value in boundary_checks.items() if key != "protected_paths_untouched" and value)
    if not boundary_checks["protected_paths_untouched"]:
        blocking.append("protected_paths_touched")
    blocking.extend(key for key, value in refresh_checks.items() if not value)
    if readiness_checks["known_owner_readiness_state"] != "blocked":
        blocking.append("owner_readiness_state_not_blocked")
    if readiness_checks["owner_operationally_acceptable"]:
        blocking.append("owner_operationally_acceptable_changed_true")
    if readiness_checks["source_readiness_score"] != 54 or readiness_checks["minimum_owner_readiness_score"] != 75 or readiness_checks["score_gap"] != 21:
        blocking.append("readiness_score_lineage_changed")
    if not readiness_checks["not_owner_readiness_gate_decision"]:
        blocking.append("go_no_go_labeled_as_gate_decision")
    blocking.extend(backfill.get("blocking_reasons", []))
    blocking.extend(recomputed.get("blocking_reasons", []))
    blocking.extend(closeout.get("blocking_reasons", []))

    warnings = [
        *discovery.get("warnings", []),
        *availability.get("warnings", []),
        *backfill.get("warnings", []),
        *recomputed.get("warnings", []),
        *closeout.get("warnings", []),
    ]
    audit = {
        "audit_id": "A-SHARE-HISTORICAL-BACKFILL-AND-REFRESH-PLANNING-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": list(dict.fromkeys(warnings)),
        "artifact_checks": artifact_checks,
        "boundary": boundary_checks,
        "refresh_checks": refresh_checks,
        "readiness_checks": readiness_checks,
        "eligible_day_count_after_backfill": backfill.get("eligible_day_count_after_backfill"),
        "target_total_evidence_days_passed": backfill.get("target_total_evidence_days_passed"),
        "go_no_go_after_backfill_decision": go_no_go.get("decision"),
        "test_policy": {"targeted_pytest_required": True, "full_pytest_run": False},
        "audit_json_path": _rel(audit_path, paths.project_root),
        "audit_markdown_path": _rel(report_path, paths.project_root),
    }
    write_json(audit_path, audit)
    _write_report(report_path, audit)
    return audit


def _write_report(path: Path, audit: dict[str, Any]) -> None:
    lines = [
        "# A-Share Historical Backfill and Refresh Planning Audit",
        "",
        "## Summary",
        f"- overall_passed: {audit['overall_passed']}",
        f"- blocking_reasons: {audit['blocking_reasons']}",
        f"- warnings_count: {len(audit['warnings'])}",
        f"- eligible_day_count_after_backfill: {audit['eligible_day_count_after_backfill']}",
        f"- target_total_evidence_days_passed: {audit['target_total_evidence_days_passed']}",
        f"- go_no_go_after_backfill_decision: {audit['go_no_go_after_backfill_decision']}",
        "",
        "## Artifact Checks",
        *[f"- {key}: {value}" for key, value in audit["artifact_checks"].items()],
        "",
        "## Boundary",
        *[f"- {key}: {value}" for key, value in audit["boundary"].items()],
        "",
        "## Refresh Checks",
        *[f"- {key}: {value}" for key, value in audit["refresh_checks"].items()],
        "",
        "## Test Policy",
        "- full_pytest_run: false",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
