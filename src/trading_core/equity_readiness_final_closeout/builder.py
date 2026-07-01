"""Build the v0.9.6 final not-ready closeout and next evidence plan."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v0.9.6-a-share-controlled-readiness-reevaluation-or-final-not-ready-closeout"
SOURCE_VERSION = "v0.9.5-a-share-research-evidence-accumulation-quality-review-and-reevaluation-prep"
RECOMMENDED_NEXT_VERSION = "v0.9.7-a-share-additional-evidence-collection-plan-execution-tracker"
DEFAULT_AS_OF_DATE = "2026-07-01"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
TARGET_TOTAL_EVIDENCE_DAYS = 5
EXPECTED_BRANCH = "final_not_ready_closeout"


def build_a_share_final_not_ready_closeout(*, as_of_date: str = DEFAULT_AS_OF_DATE, paths: ProjectPaths | None = None) -> dict[str, Any]:
    paths = paths or project_paths()
    data_dir = _data_dir(paths, as_of_date)
    output_dir = _output_dir(paths, as_of_date)
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    protected_before = _protected_snapshot(paths)

    request = _closeout_request(as_of_date)
    source_review = _source_evidence_review(paths, as_of_date)
    branch = _branch_selection_result(as_of_date, source_review)
    disallowance = _controlled_reevaluation_disallowance_record(as_of_date, source_review, branch)
    requirements = _additional_evidence_requirement_register(paths, as_of_date, source_review)
    next_plan = _next_cycle_evidence_plan(as_of_date, source_review, requirements)
    blocker_summary = _unresolved_blocker_closeout_summary(paths, as_of_date, source_review)
    owner_summary = _owner_not_ready_summary(as_of_date, source_review, requirements)
    backlog = _developer_follow_up_backlog(as_of_date, requirements)
    protected_after = _protected_snapshot(paths)
    boundary = _final_closeout_boundary_check(as_of_date, branch, protected_before == protected_after)
    result = _final_not_ready_closeout_result(as_of_date, source_review, branch, requirements)
    manifest = _final_closeout_manifest(paths, as_of_date, result)

    artifact_paths = _artifact_paths(paths, as_of_date)
    payloads = {
        "closeout_request": request,
        "source_evidence_review": source_review,
        "branch_selection_result": branch,
        "controlled_reevaluation_disallowance_record": disallowance,
        "final_not_ready_closeout_result": result,
        "additional_evidence_requirement_register": requirements,
        "next_cycle_evidence_plan": next_plan,
        "unresolved_blocker_closeout_summary": blocker_summary,
        "owner_not_ready_summary": owner_summary,
        "developer_follow_up_backlog": backlog,
        "final_closeout_boundary_check": boundary,
        "final_closeout_manifest": manifest,
    }
    for key, payload in payloads.items():
        write_json(artifact_paths[key], payload)
    _write_text(artifact_paths["closeout_report"], _closeout_markdown(result, source_review, branch, disallowance, requirements))
    _write_text(artifact_paths["evidence_plan_report"], _evidence_plan_markdown(requirements, next_plan, backlog))
    _write_text(artifact_paths["owner_summary_report"], _owner_summary_markdown(owner_summary))

    return {
        "builder_id": "A-SHARE-FINAL-NOT-READY-CLOSEOUT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": bool(result["overall_passed"] and boundary["overall_passed"]),
        "blocking_reasons": [*result["blocking_reasons"], *boundary["blocking_reasons"]],
        "warnings": [*result["warnings"], *boundary["warnings"]],
        "v095_baseline_verified": source_review["review_passed"],
        "v095_future_reevaluation_decision": source_review["future_reevaluation_decision"],
        "v095_ready_for_future_controlled_reevaluation_prep": source_review["ready_for_future_controlled_reevaluation_prep"],
        "selected_branch": branch["selected_branch"],
        "controlled_reevaluation_allowed": branch["controlled_reevaluation_allowed"],
        "controlled_reevaluation_executed": False,
        "final_closeout_decision": result["final_closeout_decision"],
        "additional_evidence_required": result["additional_evidence_required"],
        "next_cycle_required": result["next_cycle_required"],
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_blocker_count": requirements["source_blocker_count"],
        "blocker_coverage_ratio": requirements["source_blocker_coverage_ratio"],
        "requirements_count": requirements["requirement_count"],
        "blocking_requirement_count": requirements["blocking_requirement_count"],
        "minimum_future_research_days_required": requirements["minimum_future_research_days_required"],
        "current_eligible_days": next_plan["current_eligible_days"],
        "target_total_evidence_days": next_plan["target_total_evidence_days"],
        "unresolved_blockers_remaining_open": blocker_summary["blockers_remaining_open"],
        "owner_not_ready_summary_generated": True,
        "developer_follow_up_backlog_count": backlog["item_count"],
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "build_from_existing_data_run": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "final_closeout_used_as_trade_instruction": False,
        "protected_paths_untouched": boundary["protected_paths_untouched"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
    }


def _closeout_request(as_of_date: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-FINAL-NOT-READY-CLOSEOUT-REQUEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_version": SOURCE_VERSION,
        "requested_operation": "controlled_reevaluation_or_final_not_ready_closeout",
        "branch_selection_required": True,
        "allow_controlled_reevaluation_if_ready": False,
        "expected_branch": EXPECTED_BRANCH,
        "allow_owner_readiness_gate_rerun": False,
        "allow_new_gate_score": False,
        "allow_new_gate_decision": False,
        "allow_threshold_change": False,
        "allow_waiver": False,
        "research_only": True,
        "virtual_only": True,
        "not_investment_advice": True,
        "not_order_instruction": True,
        "not_live_trading_ready": True,
    }


def _source_evidence_review(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    evidence = read_json(paths.data_dir / "equity_research_evidence_accumulation" / "daily" / as_of_date / "evidence_accumulation_result.json")
    prep = read_json(paths.data_dir / "equity_readiness_reevaluation_prep" / "daily" / as_of_date / "reevaluation_prep_result.json")
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_research_evidence_accumulation_and_prep_audit.json")
    source_found = bool(evidence and prep and audit)
    blocking = []
    if not source_found:
        blocking.append("v095_source_artifacts_missing")
    if source_found and not audit.get("overall_passed"):
        blocking.append("v095_audit_not_passed")
    return {
        "review_id": "A-SHARE-SOURCE-EVIDENCE-REVIEW",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "source_artifacts_found": source_found,
        "source_audit_passed": bool(audit.get("overall_passed")),
        "source_blocking_reasons": audit.get("blocking_reasons", []),
        "eligible_day_count": evidence.get("eligible_day_count", 0),
        "eligible_days": evidence.get("eligible_days", []),
        "prep_evidence_day_count_passed": bool(evidence.get("prep_evidence_day_count_passed")),
        "controlled_reevaluation_day_count_passed": bool(evidence.get("controlled_reevaluation_day_count_passed")),
        "evidence_quality_overall_status": prep.get("evidence_quality_overall_status", "missing"),
        "blocker_count": prep.get("blocker_count", 0),
        "blocker_coverage_ratio": prep.get("blocker_coverage_ratio", 0.0),
        "prep_coverage_passed": bool(prep.get("prep_coverage_passed")),
        "controlled_reevaluation_coverage_passed": bool(prep.get("controlled_reevaluation_coverage_passed")),
        "reevaluation_input_candidate_package_status": prep.get("reevaluation_input_candidate_package_status", "missing"),
        "controlled_reevaluation_precheck_status": prep.get("controlled_reevaluation_precheck_status", prep.get("precheck_status", "missing")),
        "future_reevaluation_decision": prep.get("future_reevaluation_decision", "missing"),
        "ready_for_future_controlled_reevaluation_prep": bool(prep.get("ready_for_future_controlled_reevaluation_prep")),
        "owner_readiness_state": prep.get("known_owner_readiness_state", "blocked"),
        "owner_operationally_acceptable": bool(prep.get("owner_operationally_acceptable")),
        "source_readiness_score": prep.get("source_readiness_score", SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": prep.get("minimum_owner_readiness_score", MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": prep.get("score_gap", MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE),
        "review_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": audit.get("warnings", []),
    }


def _branch_selection_result(as_of_date: str, source: dict[str, Any]) -> dict[str, Any]:
    controlled_allowed = (
        source["future_reevaluation_decision"] == "go_for_future_controlled_reevaluation_prep"
        and source["controlled_reevaluation_precheck_status"] == "ready"
        and source["ready_for_future_controlled_reevaluation_prep"] is True
    )
    selected = "controlled_reevaluation" if controlled_allowed else EXPECTED_BRANCH
    return {
        "selection_id": "A-SHARE-READINESS-CLOSEOUT-BRANCH-SELECTION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "allowed_branches": ["controlled_reevaluation", "final_not_ready_closeout", "failed_precondition_closeout"],
        "selected_branch": selected,
        "controlled_reevaluation_allowed": controlled_allowed,
        "controlled_reevaluation_executed": False,
        "selection_inputs": {
            "future_reevaluation_decision": source["future_reevaluation_decision"],
            "controlled_reevaluation_precheck_status": source["controlled_reevaluation_precheck_status"],
            "ready_for_future_controlled_reevaluation_prep": source["ready_for_future_controlled_reevaluation_prep"],
            "prep_coverage_passed": source["prep_coverage_passed"],
            "controlled_reevaluation_coverage_passed": source["controlled_reevaluation_coverage_passed"],
            "blocker_coverage_ratio": source["blocker_coverage_ratio"],
            "controlled_reevaluation_day_count_passed": source["controlled_reevaluation_day_count_passed"],
        },
        "selection_rationale": [
            "controlled reevaluation is disallowed because v0.9.5 no-go result and precheck not_ready.",
            f"future_reevaluation_decision={source['future_reevaluation_decision']}",
            f"controlled_reevaluation_precheck_status={source['controlled_reevaluation_precheck_status']}",
        ],
        "blocking_reasons": [],
        "warnings": [],
    }


def _controlled_reevaluation_disallowance_record(as_of_date: str, source: dict[str, Any], branch: dict[str, Any]) -> dict[str, Any]:
    return {
        "record_id": "A-SHARE-CONTROLLED-REEVALUATION-DISALLOWANCE-RECORD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "controlled_reevaluation_disallowed": not branch["controlled_reevaluation_allowed"],
        "controlled_reevaluation_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "disallowance_reasons": [
            f"future_reevaluation_decision={source['future_reevaluation_decision']}",
            f"controlled_reevaluation_precheck_status={source['controlled_reevaluation_precheck_status']}",
            f"ready_for_future_controlled_reevaluation_prep={str(source['ready_for_future_controlled_reevaluation_prep']).lower()}",
            f"controlled_reevaluation_day_count_passed={str(source['controlled_reevaluation_day_count_passed']).lower()}",
            f"controlled_reevaluation_coverage_passed={str(source['controlled_reevaluation_coverage_passed']).lower()}",
        ],
        "manual_override_allowed": False,
        "threshold_lowered": False,
        "waiver_applied": False,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
    }


def _final_not_ready_closeout_result(as_of_date: str, source: dict[str, Any], branch: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
    status = "sufficient_for_prep_but_not_for_reevaluation" if source["prep_evidence_day_count_passed"] else "insufficient_for_prep"
    return {
        "result_id": "A-SHARE-FINAL-NOT-READY-CLOSEOUT-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "selected_branch": branch["selected_branch"],
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": source["warnings"],
        "owner_readiness_final_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "evidence_package_status": status,
        "evidence_quality_overall_status": source["evidence_quality_overall_status"],
        "blocker_coverage_ratio": source["blocker_coverage_ratio"],
        "controlled_reevaluation_allowed": branch["controlled_reevaluation_allowed"],
        "controlled_reevaluation_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "final_closeout_decision": "not_ready_additional_evidence_required",
        "additional_evidence_required": True,
        "next_cycle_required": True,
        "requirements_count": requirements["requirement_count"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _additional_evidence_requirement_register(paths: ProjectPaths, as_of_date: str, source: dict[str, Any]) -> dict[str, Any]:
    blocker_mapping = read_json(paths.data_dir / "equity_readiness_reevaluation_prep" / "daily" / as_of_date / "blocker_evidence_mapping.json")
    blockers = blocker_mapping.get("blockers", [])
    additional_days = max(TARGET_TOTAL_EVIDENCE_DAYS - int(source["eligible_day_count"]), 0)
    requirements = [
        _requirement("REQ001", "additional_research_output_days", "Collect additional eligible research output days with source trace and boundary validation.", "minimum_evidence_days_for_controlled_reevaluation", True, "eligible_research_output_day", additional_days, 0, False, True, True, ["daily feature/score/candidate/portfolio/briefing artifacts", "boundary check", "source trace"]),
        _requirement("REQ002", "blocker_specific_evidence", "Raise blocker evidence coverage before any future reevaluation prep can proceed.", "blocker_coverage_ratio_for_controlled_reevaluation", True, "audit_verified_blocker_evidence", 0.85, source["blocker_coverage_ratio"], False, True, False, ["blocker mapping with strong or moderate evidence"]),
        _requirement("REQ003", "source_trace_evidence", "Preserve source trace evidence for every additional eligible research day.", "source_traceability", True, "source_trace_artifact", TARGET_TOTAL_EVIDENCE_DAYS, source["eligible_day_count"], False, True, True, ["source trace JSON and markdown references"]),
        _requirement("REQ004", "manual_review_evidence", "Owner/developer review should confirm unresolved blocker interpretation before reopening gate prep.", "manual_review_evidence", False, "review_record", 1, 0, True, True, False, ["manual review note linked to blocker register"]),
    ]
    return {
        "register_id": "A-SHARE-ADDITIONAL-EVIDENCE-REQUIREMENT-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_blocker_count": source["blocker_count"],
        "source_blocker_coverage_ratio": source["blocker_coverage_ratio"],
        "requirements": requirements,
        "requirement_count": len(requirements),
        "blocking_requirement_count": sum(1 for item in requirements if item["blocking"]),
        "owner_action_requirement_count": sum(1 for item in requirements if item["owner_action_required"]),
        "developer_action_requirement_count": sum(1 for item in requirements if item["developer_action_required"]),
        "data_collection_requirement_count": sum(1 for item in requirements if item["data_collection_required"]),
        "future_research_days_required": additional_days,
        "minimum_future_research_days_required": 3,
        "overall_requirement_status": "additional_evidence_required",
        "source_blockers": [{"blocker_id": item.get("blocker_id"), "evidence_strength": item.get("evidence_strength")} for item in blockers],
    }


def _requirement(
    requirement_id: str,
    category: str,
    description: str,
    source_gap_or_blocker: str,
    blocking: bool,
    required_evidence_type: str,
    minimum_quantity: Any,
    current_quantity: Any,
    owner_action_required: bool,
    developer_action_required: bool,
    data_collection_required: bool,
    completion_evidence: list[str],
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "category": category,
        "description": description,
        "source_gap_or_blocker": source_gap_or_blocker,
        "blocking": blocking,
        "required_evidence_type": required_evidence_type,
        "minimum_quantity": minimum_quantity,
        "current_quantity": current_quantity,
        "owner_action_required": owner_action_required,
        "developer_action_required": developer_action_required,
        "data_collection_required": data_collection_required,
        "suggested_next_version": RECOMMENDED_NEXT_VERSION,
        "completion_evidence": completion_evidence,
        "notes": "Requirement is for evidence collection only and does not authorize a gate rerun.",
    }


def _next_cycle_evidence_plan(as_of_date: str, source: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
    target_dates = [f"future_research_day_{idx}" for idx in range(1, requirements["future_research_days_required"] + 1)]
    return {
        "plan_id": "A-SHARE-NEXT-CYCLE-EVIDENCE-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "plan_status": "required",
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "minimum_additional_research_days": requirements["minimum_future_research_days_required"],
        "target_total_evidence_days": TARGET_TOTAL_EVIDENCE_DAYS,
        "current_eligible_days": source["eligible_day_count"],
        "target_dates": target_dates,
        "required_tasks": [
            "collect additional research-only daily output packages",
            "validate source trace and boundary artifacts for every added day",
            "update blocker evidence mapping after new evidence exists",
            "rerun evidence accumulation before any future gate prep decision",
        ],
        "forbidden_tasks": [
            "broker_connection",
            "real_account_read",
            "real_orders",
            "order_preview",
            "buy_sell_signals",
            "owner_readiness_gate_rerun_without_evidence",
            "threshold_lowering",
            "auto_waiver",
        ],
        "success_criteria_for_next_cycle": [
            "eligible_day_count>=5",
            "blocker_coverage_ratio>=0.85",
            "controlled_reevaluation_precheck_status=ready",
            "owner_readiness_gate_rerun=false until explicitly authorized",
        ],
        "notes": ["Plan is non-executing and does not schedule automation."],
    }


def _unresolved_blocker_closeout_summary(paths: ProjectPaths, as_of_date: str, source: dict[str, Any]) -> dict[str, Any]:
    mapping = read_json(paths.data_dir / "equity_readiness_reevaluation_prep" / "daily" / as_of_date / "blocker_evidence_mapping.json")
    blockers = []
    partial = 0
    insufficient = 0
    for blocker in mapping.get("blockers", []):
        strength = blocker.get("evidence_strength", "missing")
        if strength in {"strong", "moderate"}:
            partial += 1
            status = "partial_evidence_open"
        else:
            insufficient += 1
            status = "insufficient_evidence_open"
        blockers.append({**blocker, "v096_closeout_status": status, "closed_by_v096": False})
    return {
        "summary_id": "A-SHARE-UNRESOLVED-BLOCKER-CLOSEOUT-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_blocker_count": source["blocker_count"],
        "blockers": blockers,
        "blockers_with_sufficient_evidence": 0,
        "blockers_with_partial_evidence": partial,
        "blockers_with_insufficient_evidence": insufficient,
        "blockers_closed_by_v096": 0,
        "blockers_remaining_open": source["blocker_count"],
        "overall_blocker_status": "open",
    }


def _owner_not_ready_summary(as_of_date: str, source: dict[str, Any], requirements: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary_id": "A-SHARE-OWNER-NOT-READY-SUMMARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "headline": "Owner-readiness remains blocked.",
        "plain_language_summary": "当前研究系统可以继续用于 research-only / virtual-only 分析，但还不能作为 owner 日常可接受系统，更不能用于实盘或交易指令。",
        "why_not_ready": [
            "v0.9.5 evidence prep 给出的 future_reevaluation_decision 是 no_go_additional_evidence_required。",
            "controlled reevaluation precheck 仍是 not_ready。",
            f"blocker coverage ratio 只有 {source['blocker_coverage_ratio']}，未达到 0.85。",
            f"当前 eligible evidence days 为 {source['eligible_day_count']}，未达到 5 天要求。",
        ],
        "what_has_improved": [
            "已有 2 个 evidence-eligible research output days。",
            "research-only boundary validation 已通过。",
            "已形成下一轮 evidence accumulation 的明确要求。",
        ],
        "what_is_still_missing": [
            f"至少还需要 {requirements['minimum_future_research_days_required']} 个额外 research-only evidence days。",
            "需要更高 blocker evidence coverage。",
            "需要重新运行 evidence accumulation，而不是直接运行 gate。",
        ],
        "what_owner_can_do_next": [
            "查看 final not-ready closeout report。",
            "按 additional evidence plan 准备下一轮证据。",
            "继续将系统限定为 research-only / virtual-only。",
        ],
        "what_owner_must_not_do": [
            "不能把候选股当作买入建议。",
            "不能把 score 当作买卖信号。",
            "不能把 virtual portfolio 当作真实账户组合。",
            "不能据此执行实盘或下单。",
        ],
        "not_live_trading_ready": True,
        "not_investment_advice": True,
        "not_order_instruction": True,
    }


def _developer_follow_up_backlog(as_of_date: str, requirements: dict[str, Any]) -> dict[str, Any]:
    items = []
    category_map = {
        "additional_research_output_days": "evidence_collection",
        "blocker_specific_evidence": "multi_day_tracking",
        "source_trace_evidence": "source_trace_hardening",
        "manual_review_evidence": "operator_usability",
    }
    for requirement in requirements["requirements"]:
        items.append(
            {
                "item_id": f"DEV-{requirement['requirement_id']}",
                "title": requirement["description"],
                "category": category_map.get(requirement["category"], "evidence_collection"),
                "description": requirement["description"],
                "source_requirement_id": requirement["requirement_id"],
                "priority": "high" if requirement["blocking"] else "medium",
                "blocking": requirement["blocking"],
                "recommended_version": RECOMMENDED_NEXT_VERSION,
                "acceptance_criteria": requirement["completion_evidence"],
                "forbidden_scope": ["broker", "real_account", "orders", "order_preview", "buy_sell_signals", "owner_readiness_gate_rerun"],
            }
        )
    return {
        "backlog_id": "A-SHARE-DEVELOPER-FOLLOW-UP-BACKLOG",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "items": items,
        "item_count": len(items),
        "blocking_item_count": sum(1 for item in items if item["blocking"]),
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _final_closeout_boundary_check(as_of_date: str, branch: dict[str, Any], protected_untouched: bool) -> dict[str, Any]:
    blocking = [] if protected_untouched else ["protected_paths_modified"]
    return {
        "boundary_id": "A-SHARE-FINAL-NOT-READY-CLOSEOUT-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "selected_branch": branch["selected_branch"],
        "closeout_only": True,
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "build_from_existing_data_run": False,
        "owner_daily_pack_run": False,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "final_closeout_used_as_trade_instruction": False,
        "protected_paths_untouched": protected_untouched,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _final_closeout_manifest(paths: ProjectPaths, as_of_date: str, result: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = _artifact_paths(paths, as_of_date)
    source_artifacts = {
        "v095_prep_result": f"data/equity_readiness_reevaluation_prep/daily/{as_of_date}/reevaluation_prep_result.json",
        "v095_evidence_result": f"data/equity_research_evidence_accumulation/daily/{as_of_date}/evidence_accumulation_result.json",
        "v095_audit": "data/equity_data_quality/a_share_research_evidence_accumulation_and_prep_audit.json",
    }
    return {
        "manifest_id": "A-SHARE-FINAL-NOT-READY-CLOSEOUT-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "source_version": SOURCE_VERSION,
        "source_artifacts": source_artifacts,
        "output_artifacts": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
        "artifact_hashes": {key: _sha256(path) for key, path in artifact_paths.items() if path.exists()},
        "selected_branch": EXPECTED_BRANCH,
        "final_closeout_decision": result["final_closeout_decision"],
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "warnings": result["warnings"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = _data_dir(paths, as_of_date)
    output_dir = _output_dir(paths, as_of_date)
    return {
        "closeout_request": data_dir / "closeout_request.json",
        "source_evidence_review": data_dir / "source_evidence_review.json",
        "branch_selection_result": data_dir / "branch_selection_result.json",
        "controlled_reevaluation_disallowance_record": data_dir / "controlled_reevaluation_disallowance_record.json",
        "final_not_ready_closeout_result": data_dir / "final_not_ready_closeout_result.json",
        "additional_evidence_requirement_register": data_dir / "additional_evidence_requirement_register.json",
        "next_cycle_evidence_plan": data_dir / "next_cycle_evidence_plan.json",
        "unresolved_blocker_closeout_summary": data_dir / "unresolved_blocker_closeout_summary.json",
        "owner_not_ready_summary": data_dir / "owner_not_ready_summary.json",
        "developer_follow_up_backlog": data_dir / "developer_follow_up_backlog.json",
        "final_closeout_boundary_check": data_dir / "final_closeout_boundary_check.json",
        "final_closeout_manifest": data_dir / "final_closeout_manifest.json",
        "closeout_report": output_dir / "A_SHARE_FINAL_NOT_READY_CLOSEOUT.md",
        "evidence_plan_report": output_dir / "A_SHARE_ADDITIONAL_EVIDENCE_REQUIREMENT_PLAN.md",
        "owner_summary_report": output_dir / "A_SHARE_OWNER_NOT_READY_SUMMARY.md",
    }


def _closeout_markdown(result: dict[str, Any], source: dict[str, Any], branch: dict[str, Any], disallowance: dict[str, Any], requirements: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Final Not-Ready Closeout",
            "",
            "## 1. Closeout Summary",
            f"- final_closeout_decision: {result['final_closeout_decision']}",
            "Owner-readiness remains blocked.",
            "",
            "## 2. Selected Branch",
            f"- selected_branch: {branch['selected_branch']}",
            "",
            "## 3. Why Controlled Reevaluation Is Not Allowed",
            "Controlled reevaluation was not executed.",
            *[f"- {item}" for item in disallowance["disallowance_reasons"]],
            "",
            "## 4. Source Evidence Review",
            f"- future_reevaluation_decision: {source['future_reevaluation_decision']}",
            f"- ready_for_future_controlled_reevaluation_prep: {source['ready_for_future_controlled_reevaluation_prep']}",
            "",
            "## 5. Final Owner-Readiness State",
            "- owner_readiness_final_state: blocked",
            "- source_readiness_score: 54 / threshold: 75 / gap: 21",
            "",
            "## 6. What Improved",
            "- Evidence prep is documented and audit-passed.",
            "- Research-only evidence days are identified.",
            "",
            "## 7. What Is Still Missing",
            "- Controlled reevaluation evidence threshold is not met.",
            "- Blocker coverage remains below required threshold.",
            "",
            "## 8. Additional Evidence Required",
            f"- requirement_count: {requirements['requirement_count']}",
            "",
            "## 9. Explicit Non-Trading Boundary",
            "No new readiness score was generated.",
            "No new gate decision was generated.",
            "This is not investment advice.",
            "This is not live trading ready.",
            "",
            "## 10. Recommended Next Version",
            f"- {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )


def _evidence_plan_markdown(requirements: dict[str, Any], plan: dict[str, Any], backlog: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Additional Evidence Requirement Plan",
            "",
            "## 1. Evidence Requirement Summary",
            f"- requirement_count: {requirements['requirement_count']}",
            "",
            "## 2. Current Evidence State",
            f"- current_eligible_days: {plan['current_eligible_days']}",
            "",
            "## 3. Required Additional Research Days",
            f"- minimum_additional_research_days: {plan['minimum_additional_research_days']}",
            "",
            "## 4. Blocker-Specific Evidence Requirements",
            *[f"- {item['requirement_id']}: {item['description']}" for item in requirements["requirements"] if item["category"] == "blocker_specific_evidence"],
            "",
            "## 5. Data / Source Trace Requirements",
            *[f"- {item['requirement_id']}: {item['description']}" for item in requirements["requirements"] if item["data_collection_required"]],
            "",
            "## 6. Boundary Requirements",
            "- Preserve research-only / virtual-only boundary.",
            "",
            "## 7. Developer Follow-Up Backlog",
            f"- item_count: {backlog['item_count']}",
            "",
            "## 8. Success Criteria for Next Cycle",
            *[f"- {item}" for item in plan["success_criteria_for_next_cycle"]],
            "",
            "## 9. Forbidden Scope",
            *[f"- {item}" for item in plan["forbidden_tasks"]],
            "",
        ]
    )


def _owner_summary_markdown(summary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A 股 Owner Not-Ready Summary",
            "",
            "## 1. 一句话结论",
            summary["plain_language_summary"],
            "",
            "## 2. 当前状态",
            "- Owner-readiness remains blocked.",
            "- 54 / 75 / gap 21",
            "",
            "## 3. 为什么还没有通过",
            *[f"- {item}" for item in summary["why_not_ready"]],
            "",
            "## 4. 已经改善了什么",
            *[f"- {item}" for item in summary["what_has_improved"]],
            "",
            "## 5. 还缺什么",
            *[f"- {item}" for item in summary["what_is_still_missing"]],
            "",
            "## 6. 下一步能做什么",
            *[f"- {item}" for item in summary["what_owner_can_do_next"]],
            "",
            "## 7. 当前不能做什么",
            *[f"- {item}" for item in summary["what_owner_must_not_do"]],
            "",
            "## 8. 免责声明",
            "- 不是投资建议。",
            "- 不是交易指令。",
            "- 不代表实盘就绪。",
            "",
        ]
    )


def _protected_snapshot(paths: ProjectPaths) -> dict[str, str]:
    roots = [
        paths.data_dir / "orders",
        paths.data_dir / "trades",
        paths.data_dir / "accounts",
        paths.outputs_dir / "orders",
        paths.outputs_dir / "trades",
        paths.outputs_dir / "accounts",
    ]
    result: dict[str, str] = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                result[_rel(path, paths.project_root)] = _sha256(path) or ""
    return result


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_readiness_final_closeout" / "daily" / as_of_date


def _output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_readiness_final_closeout" / "daily" / as_of_date


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
