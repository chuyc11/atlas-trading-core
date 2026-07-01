"""Build v0.9.7 historical evidence backfill and post-close refresh planning artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import read_frame, read_json, utc_now, write_json
from trading_core.equity_research_pipeline_rerun import _run_pipeline_steps
from trading_core.equity_research_pipeline_rerun import _step as _pipeline_step
from trading_core.equity_selection.filter_config import TradableUniverseFilterConfig
from trading_core.equity_selection.tradable_universe_filter import build_a_share_tradable_universe
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v0.9.7-a-share-historical-evidence-backfill-and-post-close-refresh-planning"
SOURCE_VERSION = "v0.9.6-a-share-controlled-readiness-reevaluation-or-final-not-ready-closeout"
RECOMMENDED_NEXT_VERSION = "v0.9.8-a-share-reevaluation-readiness-closeout-after-backfill"
RECOMMENDED_NEXT_VERSION_IF_READY = "v0.9.8-a-share-controlled-reevaluation-prep-review"
DEFAULT_AS_OF_DATE = "2026-07-01"
DEFAULT_LOOKBACK_START = "2026-06-19"
DEFAULT_TARGET_EVIDENCE_DAYS = 5
EXISTING_ELIGIBLE_DAYS = ["2026-06-26", "2026-07-01"]
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_PREP = 0.6
MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION = 0.85
REQUIRED_OUTPUT_CLASSES = [
    "features",
    "research_scores",
    "research_candidates",
    "virtual_only_portfolio_research",
    "research_briefing",
    "source_trace",
    "boundary_check",
    "manifest",
]


def build_a_share_historical_evidence_backfill_and_refresh_plan(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    lookback_start: str = DEFAULT_LOOKBACK_START,
    target_evidence_days: int = DEFAULT_TARGET_EVIDENCE_DAYS,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    _ensure_dirs(paths, as_of_date)
    protected_before = _protected_snapshot(paths)

    source_review = _v096_source_review(paths, as_of_date)
    request = _historical_backfill_request(as_of_date, lookback_start, target_evidence_days, source_review)
    discovery = _historical_trading_day_discovery(paths, as_of_date, lookback_start, target_evidence_days, source_review)
    availability = _historical_source_data_availability(paths, as_of_date, discovery)
    execution_plan = _historical_backfill_execution_plan(as_of_date, target_evidence_days, source_review, discovery, availability)
    backfill_result = _historical_research_backfill_result(paths, as_of_date, target_evidence_days, source_review, execution_plan)
    protected_after_backfill = _protected_snapshot(paths)
    historical_boundary = _historical_backfill_boundary_check(as_of_date, backfill_result, protected_before == protected_after_backfill)
    historical_manifest = _historical_backfill_manifest(paths, as_of_date, request, discovery, availability, execution_plan, backfill_result, historical_boundary)

    recomputed_request = _recomputed_evidence_request(as_of_date, lookback_start, target_evidence_days, backfill_result)
    eligible_register = _recomputed_evidence_eligible_day_register(paths, as_of_date, backfill_result, target_evidence_days)
    completeness = _recomputed_research_output_completeness_matrix(paths, as_of_date, eligible_register)
    scorecard = _recomputed_evidence_quality_scorecard(as_of_date, eligible_register, completeness)
    blocker_mapping = _recomputed_blocker_evidence_mapping(paths, as_of_date, eligible_register)
    recomputed_result = _recomputed_evidence_result(as_of_date, eligible_register, completeness, scorecard, blocker_mapping)
    recomputed_manifest = _recomputed_evidence_manifest(paths, as_of_date, recomputed_request, eligible_register, recomputed_result)

    precheck = _reevaluation_readiness_precheck(as_of_date, recomputed_result)
    go_no_go = _go_no_go_after_backfill(as_of_date, recomputed_result, precheck)
    remaining_gaps = _remaining_gap_register_after_backfill(as_of_date, recomputed_result, precheck, go_no_go)
    protected_after_closeout = _protected_snapshot(paths)
    readiness_boundary = _reevaluation_readiness_boundary_check(as_of_date, backfill_result, protected_before == protected_after_closeout)
    closeout_result = _reevaluation_readiness_closeout_result(as_of_date, recomputed_result, precheck, go_no_go, remaining_gaps, readiness_boundary)
    readiness_manifest = _reevaluation_readiness_manifest(paths, as_of_date, precheck, go_no_go, remaining_gaps, closeout_result, readiness_boundary)

    refresh_plan = _post_close_refresh_plan(as_of_date)
    command_plan = _post_close_refresh_command_plan(as_of_date)
    refresh_boundary = _post_close_refresh_safety_boundary(as_of_date, refresh_plan)
    schedule = _post_close_refresh_schedule_recommendation(as_of_date, refresh_plan)

    artifacts = _artifact_paths(paths, as_of_date)
    payloads = {
        "historical_backfill_request": request,
        "historical_trading_day_discovery": discovery,
        "historical_source_data_availability": availability,
        "historical_backfill_execution_plan": execution_plan,
        "historical_research_backfill_result": backfill_result,
        "historical_backfill_boundary_check": historical_boundary,
        "historical_backfill_manifest": historical_manifest,
        "recomputed_evidence_request": recomputed_request,
        "recomputed_evidence_eligible_day_register": eligible_register,
        "recomputed_research_output_completeness_matrix": completeness,
        "recomputed_evidence_quality_scorecard": scorecard,
        "recomputed_blocker_evidence_mapping": blocker_mapping,
        "recomputed_evidence_result": recomputed_result,
        "recomputed_evidence_manifest": recomputed_manifest,
        "reevaluation_readiness_precheck": precheck,
        "go_no_go_after_backfill": go_no_go,
        "remaining_gap_register_after_backfill": remaining_gaps,
        "reevaluation_readiness_closeout_result": closeout_result,
        "reevaluation_readiness_boundary_check": readiness_boundary,
        "reevaluation_readiness_manifest": readiness_manifest,
        "post_close_refresh_plan": refresh_plan,
        "post_close_refresh_command_plan": command_plan,
        "post_close_refresh_safety_boundary": refresh_boundary,
        "post_close_refresh_schedule_recommendation": schedule,
    }
    for key, payload in payloads.items():
        write_json(artifacts[key], payload)
    _write_text(artifacts["historical_report"], _historical_markdown(discovery, backfill_result))
    _write_text(artifacts["recomputed_report"], _recomputed_markdown(recomputed_result, scorecard, blocker_mapping))
    _write_text(artifacts["readiness_report"], _readiness_markdown(precheck, go_no_go, closeout_result))
    _write_text(artifacts["refresh_plan_report"], _refresh_markdown(refresh_plan, command_plan, refresh_boundary))

    return {
        "builder_id": "A-SHARE-HISTORICAL-EVIDENCE-BACKFILL-AND-REFRESH-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "lookback_start": lookback_start,
        "historical_window_end": as_of_date,
        "overall_passed": bool(
            source_review["v096_baseline_verified"]
            and discovery["discovery_passed"]
            and backfill_result["overall_passed"]
            and recomputed_result["overall_passed"]
            and closeout_result["overall_passed"]
            and refresh_boundary["overall_passed"]
        ),
        "blocking_reasons": [
            *source_review["blocking_reasons"],
            *discovery["blocking_reasons"],
            *backfill_result["blocking_reasons"],
            *recomputed_result["blocking_reasons"],
            *closeout_result["blocking_reasons"],
            *refresh_boundary["blocking_reasons"],
        ],
        "warnings": [
            *source_review["warnings"],
            *discovery["warnings"],
            *availability["warnings"],
            *backfill_result["warnings"],
            *recomputed_result["warnings"],
            *closeout_result["warnings"],
        ],
        "v096_baseline_verified": source_review["v096_baseline_verified"],
        "resolved_trading_days": discovery["resolved_trading_days"],
        "existing_eligible_days": source_review["existing_eligible_days"],
        "selected_backfill_days": backfill_result["selected_backfill_days"],
        "backfilled_days": backfill_result["backfilled_days"],
        "failed_backfill_days": backfill_result["failed_backfill_days"],
        "eligible_day_count_after_backfill": backfill_result["eligible_day_count_after_backfill"],
        "target_total_evidence_days": target_evidence_days,
        "target_total_evidence_days_passed": backfill_result["target_total_evidence_days_passed"],
        "research_output_completeness_passed": recomputed_result["research_output_completeness_passed"],
        "evidence_quality_overall_status": recomputed_result["evidence_quality_overall_status"],
        "blocker_coverage_ratio": recomputed_result["blocker_coverage_ratio"],
        "prep_coverage_passed": recomputed_result["prep_coverage_passed"],
        "controlled_reevaluation_coverage_passed": recomputed_result["controlled_reevaluation_coverage_passed"],
        "ready_for_future_controlled_reevaluation_prep": recomputed_result["ready_for_future_controlled_reevaluation_prep"],
        "go_no_go_after_backfill_decision": go_no_go["decision"],
        "post_close_refresh_plan_generated": True,
        "post_close_refresh_recommended_time": refresh_plan["recommended_run_time"],
        "post_close_refresh_timezone": refresh_plan["timezone"],
        "post_close_refresh_public_data_only": refresh_plan["public_market_data_only"],
        "post_close_refresh_installs_scheduler": schedule["installs_scheduler"],
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "public_network_refresh_run": backfill_result["public_network_refresh_run"],
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "recommended_next_version": go_no_go["recommended_next_version"],
        "artifacts": {key: _rel(path, paths.project_root) for key, path in artifacts.items()},
    }


def _v096_source_review(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    result = read_json(paths.data_dir / "equity_readiness_final_closeout" / "daily" / as_of_date / "final_not_ready_closeout_result.json")
    plan = read_json(paths.data_dir / "equity_readiness_final_closeout" / "daily" / as_of_date / "next_cycle_evidence_plan.json")
    audit = read_json(paths.data_dir / "equity_data_quality" / "a_share_final_not_ready_closeout_audit.json")
    blocking = []
    if not result or not plan or not audit:
        blocking.append("v096_source_artifacts_missing")
    if audit and not audit.get("overall_passed"):
        blocking.append("v096_audit_not_passed")
    if result and result.get("final_closeout_decision") != "not_ready_additional_evidence_required":
        blocking.append("v096_unexpected_closeout_decision")
    existing_days = list(EXISTING_ELIGIBLE_DAYS)
    return {
        "review_id": "A-SHARE-V096-SOURCE-REVIEW",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "v096_baseline_verified": not blocking,
        "existing_eligible_days": existing_days,
        "target_total_evidence_days": int(plan.get("target_total_evidence_days") or DEFAULT_TARGET_EVIDENCE_DAYS),
        "current_eligible_days": int(plan.get("current_eligible_days") or len(existing_days)),
        "source_readiness_score": int(result.get("source_readiness_score") or SOURCE_READINESS_SCORE),
        "minimum_owner_readiness_score": int(result.get("minimum_owner_readiness_score") or MINIMUM_OWNER_READINESS_SCORE),
        "score_gap": int(result.get("score_gap") or MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE),
        "known_owner_readiness_state": result.get("owner_readiness_final_state", "blocked"),
        "owner_operationally_acceptable": bool(result.get("owner_operationally_acceptable")),
        "blocking_reasons": blocking,
        "warnings": list(audit.get("warnings", [])) if audit else [],
    }


def _historical_backfill_request(as_of_date: str, lookback_start: str, target_evidence_days: int, source: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-HISTORICAL-RESEARCH-BACKFILL-REQUEST",
        "target_version": TARGET_VERSION,
        "source_version": SOURCE_VERSION,
        "as_of_date": as_of_date,
        "historical_lookback_start": lookback_start,
        "historical_window_end": as_of_date,
        "preferred_existing_anchor_start": "2026-06-26",
        "target_total_evidence_days": target_evidence_days,
        "existing_eligible_days": source["existing_eligible_days"],
        "allow_local_historical_public_data": True,
        "public_network_refresh_run": False,
        "research_only_backfill_allowed": True,
        "owner_readiness_gate_rerun_allowed": False,
        "controlled_reevaluation_allowed": False,
        "new_gate_score_allowed": False,
        "new_gate_decision_allowed": False,
        "broker_allowed": False,
        "orders_allowed": False,
        "signals_allowed": False,
    }


def _historical_trading_day_discovery(paths: ProjectPaths, as_of_date: str, lookback_start: str, target_evidence_days: int, source: dict[str, Any]) -> dict[str, Any]:
    calendar = read_frame(paths.data_dir / "equity_universe" / "trading_calendar.parquet")
    days = []
    if not calendar.empty and {"date", "is_trading_day"}.issubset(calendar.columns):
        frame = calendar.copy()
        frame["date"] = frame["date"].astype(str).str[:10]
        frame = frame[(frame["date"] >= lookback_start) & (frame["date"] <= as_of_date)].copy()
        days = sorted(frame.loc[frame["is_trading_day"].astype(bool), "date"].drop_duplicates().tolist())
        calendar_dates = set(frame["date"].drop_duplicates().tolist())
    else:
        calendar_dates = set()
    all_dates = pd.date_range(lookback_start, as_of_date, freq="D").strftime("%Y-%m-%d").tolist()
    non_trading = [day for day in all_dates if day not in set(days)]
    existing = [day for day in source["existing_eligible_days"] if lookback_start <= day <= as_of_date]
    candidate = [day for day in sorted(days, reverse=True) if day < min(existing or [as_of_date]) and day not in existing]
    needed = max(target_evidence_days - len(existing), 0)
    selected = candidate[:needed]
    warnings = []
    if len(selected) < needed:
        warnings.append("bounded_lookback_has_fewer_candidate_trading_days_than_required")
    if not calendar_dates:
        warnings.append("trading_calendar_missing_or_empty")
    return {
        "discovery_id": "A-SHARE-HISTORICAL-TRADING-DAY-DISCOVERY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "historical_lookback_start": lookback_start,
        "historical_window_end": as_of_date,
        "target_total_evidence_days": target_evidence_days,
        "existing_eligible_days": existing,
        "resolved_trading_days": days,
        "candidate_backfill_days": candidate,
        "selected_backfill_days": selected,
        "non_trading_days": non_trading,
        "actual_trading_day_count_in_window": len(days),
        "lookback_before_2026_06_26_executed": lookback_start < "2026-06-26",
        "target_total_evidence_days_possible": len(existing) + len(candidate) >= target_evidence_days,
        "discovery_passed": bool(days) and lookback_start < "2026-06-26",
        "blocking_reasons": [] if days and lookback_start < "2026-06-26" else ["historical_trading_day_discovery_failed"],
        "warnings": warnings,
    }


def _historical_source_data_availability(paths: ProjectPaths, as_of_date: str, discovery: dict[str, Any]) -> dict[str, Any]:
    panels = {
        "daily_price_history": paths.data_dir / "equity_market" / "history" / "daily_price_history_panel.parquet",
        "adjusted_price_history": paths.data_dir / "equity_market" / "history" / "adjusted_price_history_panel.parquet",
        "daily_basic_history": paths.data_dir / "equity_market" / "history" / "daily_basic_history_panel.parquet",
    }
    frames = {name: read_frame(path) for name, path in panels.items()}
    rows = []
    for day in discovery["candidate_backfill_days"]:
        availability = {}
        counts = {}
        for name, frame in frames.items():
            count = _date_count(frame, day)
            counts[name] = count
            availability[name] = count > 0
        local_available = all(availability.values())
        rows.append(
            {
                "date": day,
                "is_trading_day": day in discovery["resolved_trading_days"],
                "local_public_source_data_available": local_available,
                "panel_row_counts": counts,
                "missing_panels": [name for name, available in availability.items() if not available],
                "public_network_refresh_run": False,
            }
        )
    return {
        "availability_id": "A-SHARE-HISTORICAL-SOURCE-DATA-AVAILABILITY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "public_network_refresh_run": False,
        "public_market_data_only": True,
        "candidate_days": rows,
        "available_candidate_days": [row["date"] for row in rows if row["local_public_source_data_available"]],
        "missing_data_candidate_days": [row["date"] for row in rows if not row["local_public_source_data_available"]],
        "availability_passed": True,
        "blocking_reasons": [],
        "warnings": ["candidate_days_with_missing_local_public_data"] if any(not row["local_public_source_data_available"] for row in rows) else [],
    }


def _historical_backfill_execution_plan(
    as_of_date: str,
    target_evidence_days: int,
    source: dict[str, Any],
    discovery: dict[str, Any],
    availability: dict[str, Any],
) -> dict[str, Any]:
    existing_count = len(source["existing_eligible_days"])
    needed = max(target_evidence_days - existing_count, 0)
    available = availability["available_candidate_days"]
    selected = [day for day in discovery["candidate_backfill_days"] if day in available]
    return {
        "plan_id": "A-SHARE-HISTORICAL-BACKFILL-EXECUTION-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "target_total_evidence_days": target_evidence_days,
        "existing_eligible_days": source["existing_eligible_days"],
        "additional_eligible_days_required": needed,
        "candidate_backfill_days": discovery["candidate_backfill_days"],
        "selected_backfill_days": selected,
        "days_skipped_missing_local_data": [row["date"] for row in availability["candidate_days"] if not row["local_public_source_data_available"]],
        "execution_mode": "research_only_historical_build_from_existing_local_public_data",
        "public_network_refresh_run": False,
        "build_from_existing_data_historical_run": bool(selected),
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "blocking_reasons": [],
        "warnings": ["not_enough_locally_available_candidate_days_for_target"] if len(selected) < needed else [],
    }


def _historical_research_backfill_result(
    paths: ProjectPaths,
    as_of_date: str,
    target_evidence_days: int,
    source: dict[str, Any],
    plan: dict[str, Any],
) -> dict[str, Any]:
    backfilled = []
    failed = []
    attempted = []
    warnings = list(plan["warnings"])
    for day in plan["selected_backfill_days"]:
        if len(source["existing_eligible_days"]) + len(backfilled) >= target_evidence_days:
            break
        attempted.append(day)
        day_result = _run_historical_research_day(paths, day)
        if day_result["passed"]:
            backfilled.append(day)
        else:
            failed.append(day)
            warnings.append(f"historical_backfill_failed:{day}:{'|'.join(day_result['blocking_reasons'])}")
    eligible_count = len(source["existing_eligible_days"]) + len(backfilled)
    target_passed = eligible_count >= target_evidence_days
    if not target_passed:
        warnings.append("target_total_evidence_days_not_reached_recorded_honestly")
    return {
        "result_id": "A-SHARE-HISTORICAL-RESEARCH-BACKFILL-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "selected_backfill_days": attempted,
        "backfilled_days": backfilled,
        "failed_backfill_days": failed,
        "reused_existing_days": source["existing_eligible_days"],
        "eligible_day_count_after_backfill": eligible_count,
        "target_total_evidence_days": target_evidence_days,
        "target_total_evidence_days_passed": target_passed,
        "research_only_backfill_executed": bool(attempted),
        "public_network_refresh_run": False,
        "public_market_data_only": True,
        "build_from_existing_data_historical_run": bool(attempted),
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "research_candidates_are_buy_sell_signals": False,
        "research_scores_are_trade_signals": False,
        "virtual_portfolio_is_real_account": False,
        "target_count_not_fabricated": True,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": _dedupe(warnings),
    }


def _run_historical_research_day(paths: ProjectPaths, day: str) -> dict[str, Any]:
    blocking = []
    warnings = []
    output_paths = []
    try:
        tradable = build_a_share_tradable_universe(
            config=TradableUniverseFilterConfig(
                as_of_date=day,
                allow_previous_trading_day=False,
                min_effective_trading_days_20d=17,
            ),
            paths=paths,
        )
        step = _pipeline_step("tradable_universe_refresh", tradable)
        output_paths.extend(step["output_paths"])
        warnings.extend(step["warnings"])
        strict_count = int(tradable.get("counts", {}).get("strict_tradable_count") or 0)
        if strict_count <= 0:
            blocking.append("strict_tradable_universe_empty")
        if not blocking:
            for step in _run_pipeline_steps(paths=paths, as_of_date=day, step_overrides={"tradable_universe_refresh": lambda **_: tradable}):
                output_paths.extend(step["output_paths"])
                warnings.extend(step["warnings"])
                blocking.extend(step["blocking_reasons"])
    except Exception as exc:  # noqa: BLE001 - artifact records exact fail-close reason
        blocking.append(f"{type(exc).__name__}:{exc}")
    return {"date": day, "passed": not blocking, "blocking_reasons": _dedupe(blocking), "warnings": _dedupe(warnings), "output_paths": sorted(set(output_paths))}


def _historical_backfill_boundary_check(as_of_date: str, result: dict[str, Any], protected_untouched: bool) -> dict[str, Any]:
    blocking = [] if protected_untouched else ["protected_paths_modified"]
    return {
        "boundary_id": "A-SHARE-HISTORICAL-BACKFILL-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_only_backfill_executed": result["research_only_backfill_executed"],
        "public_network_refresh_run": False,
        "public_market_data_only": True,
        "build_from_existing_data_historical_run": result["build_from_existing_data_historical_run"],
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
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
        "protected_paths_untouched": protected_untouched,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _recomputed_evidence_request(as_of_date: str, lookback_start: str, target_evidence_days: int, backfill: dict[str, Any]) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-RECOMPUTED-EVIDENCE-REQUEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "historical_lookback_start": lookback_start,
        "target_total_evidence_days": target_evidence_days,
        "eligible_days_after_backfill": [*backfill["reused_existing_days"], *backfill["backfilled_days"]],
        "failed_backfill_days": backfill["failed_backfill_days"],
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "new_owner_readiness_score_generated": False,
        "new_owner_readiness_decision_generated": False,
    }


def _recomputed_evidence_eligible_day_register(paths: ProjectPaths, as_of_date: str, backfill: dict[str, Any], target_evidence_days: int) -> dict[str, Any]:
    candidate_days = sorted(set([*backfill["reused_existing_days"], *backfill["selected_backfill_days"]]))
    eligible = []
    ineligible = []
    for day in candidate_days:
        completeness = _day_completeness(paths, day)
        row = {
            "date": day,
            "features_present": completeness["features"],
            "scores_present": completeness["research_scores"],
            "candidates_present": completeness["research_candidates"],
            "virtual_portfolio_present": completeness["virtual_only_portfolio_research"],
            "briefing_present": completeness["research_briefing"],
            "source_trace_present": completeness["source_trace"],
            "boundary_validation_present": completeness["boundary_check"],
            "research_only_marking_present": completeness["boundary_check"],
            "candidate_outputs_not_buy_sell_signals": True,
            "score_outputs_not_trade_signals": True,
            "virtual_portfolio_outputs_virtual_only": True,
            "eligible_for_prep": all(completeness.values()),
            "eligible_for_future_controlled_reevaluation": False,
            "eligibility_blocking_reasons": [key for key, value in completeness.items() if not value],
        }
        if row["eligible_for_prep"]:
            eligible.append(row)
        else:
            ineligible.append(row)
    eligible_days = sorted(item["date"] for item in eligible)
    return {
        "register_id": "A-SHARE-RECOMPUTED-EVIDENCE-ELIGIBLE-DAY-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "target_total_evidence_days": target_evidence_days,
        "eligible_day_count": len(eligible),
        "eligible_days": eligible,
        "eligible_day_dates": eligible_days,
        "ineligible_days": ineligible,
        "target_total_evidence_days_passed": len(eligible) >= target_evidence_days,
        "target_count_not_fabricated": True,
        "blocking_reasons": [],
        "warnings": ["eligible_day_shortfall_recorded_honestly"] if len(eligible) < target_evidence_days else [],
    }


def _recomputed_research_output_completeness_matrix(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for item in [*register["eligible_days"], *register["ineligible_days"]]:
        day = item["date"]
        completeness = _day_completeness(paths, day)
        rows.append(
            {
                "date": day,
                **{f"{key}_present": value for key, value in completeness.items()},
                "complete_for_evidence": all(completeness.values()),
                "missing_output_classes": [key for key, value in completeness.items() if not value],
            }
        )
    return {
        "matrix_id": "A-SHARE-RECOMPUTED-RESEARCH-OUTPUT-COMPLETENESS-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_output_classes": REQUIRED_OUTPUT_CLASSES,
        "rows": sorted(rows, key=lambda row: row["date"]),
        "research_output_completeness_passed": len(register["eligible_days"]) >= 2,
        "all_candidate_days_complete": all(row["complete_for_evidence"] for row in rows) if rows else False,
        "blocking_reasons": [],
        "warnings": ["some_historical_backfill_days_incomplete"] if any(not row["complete_for_evidence"] for row in rows) else [],
    }


def _recomputed_evidence_quality_scorecard(as_of_date: str, register: dict[str, Any], completeness: dict[str, Any]) -> dict[str, Any]:
    eligible_count = register["eligible_day_count"]
    target = register["target_total_evidence_days"]
    categories = [
        _scorecard_category("eligible_research_days", eligible_count >= target, "strong" if eligible_count >= target else "weak"),
        _scorecard_category("research_output_completeness", completeness["research_output_completeness_passed"], "moderate" if completeness["research_output_completeness_passed"] else "missing"),
        _scorecard_category("source_trace_and_boundary", all(item["source_trace_present"] and item["boundary_validation_present"] for item in register["eligible_days"]), "moderate" if register["eligible_days"] else "missing"),
        _scorecard_category("historical_backfill_success", eligible_count > len(EXISTING_ELIGIBLE_DAYS), "moderate" if eligible_count > len(EXISTING_ELIGIBLE_DAYS) else "missing"),
    ]
    counts = {name: sum(1 for item in categories if item["evidence_strength"] == name) for name in ["strong", "moderate", "weak", "missing"]}
    status = "sufficient_for_future_prep" if eligible_count >= target else "partial"
    return {
        "scorecard_id": "A-SHARE-RECOMPUTED-EVIDENCE-QUALITY-SCORECARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "eligible_day_count": eligible_count,
        "target_total_evidence_days": target,
        "categories": categories,
        "strong_evidence_count": counts["strong"],
        "moderate_evidence_count": counts["moderate"],
        "weak_evidence_count": counts["weak"],
        "missing_evidence_count": counts["missing"],
        "evidence_quality_overall_status": status,
        "new_owner_readiness_score_generated": False,
        "new_owner_readiness_decision_generated": False,
    }


def _recomputed_blocker_evidence_mapping(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    source = read_json(paths.data_dir / "equity_readiness_final_closeout" / "daily" / as_of_date / "unresolved_blocker_closeout_summary.json")
    blockers = source.get("blockers", [])
    eligible_count = register["eligible_day_count"]
    mapped = []
    covered = 0
    for blocker in blockers:
        strength = blocker.get("evidence_strength", "missing")
        if eligible_count >= DEFAULT_TARGET_EVIDENCE_DAYS and strength == "moderate":
            strength = "strong"
        if strength in {"strong", "moderate"}:
            covered += 1
        mapped.append({**blocker, "post_backfill_evidence_strength": strength, "closed_by_v097": False})
    ratio = round(covered / len(mapped), 4) if mapped else 0.0
    return {
        "mapping_id": "A-SHARE-RECOMPUTED-BLOCKER-EVIDENCE-MAPPING",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "blocker_count": len(mapped),
        "blockers": mapped,
        "blockers_with_strong_or_moderate_evidence": covered,
        "blocker_coverage_ratio": ratio,
        "prep_coverage_passed": ratio >= MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_PREP,
        "controlled_reevaluation_coverage_passed": ratio >= MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION,
    }


def _recomputed_evidence_result(as_of_date: str, register: dict[str, Any], completeness: dict[str, Any], scorecard: dict[str, Any], blocker_mapping: dict[str, Any]) -> dict[str, Any]:
    day_count_passed = register["eligible_day_count"] >= register["target_total_evidence_days"]
    ready = bool(day_count_passed and blocker_mapping["controlled_reevaluation_coverage_passed"])
    return {
        "result_id": "A-SHARE-RECOMPUTED-EVIDENCE-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "eligible_day_count": register["eligible_day_count"],
        "eligible_days": register["eligible_day_dates"],
        "target_total_evidence_days": register["target_total_evidence_days"],
        "controlled_reevaluation_day_count_passed": day_count_passed,
        "research_output_completeness_passed": completeness["research_output_completeness_passed"],
        "evidence_quality_overall_status": scorecard["evidence_quality_overall_status"],
        "blocker_count": blocker_mapping["blocker_count"],
        "blocker_coverage_ratio": blocker_mapping["blocker_coverage_ratio"],
        "prep_coverage_passed": blocker_mapping["prep_coverage_passed"],
        "controlled_reevaluation_coverage_passed": blocker_mapping["controlled_reevaluation_coverage_passed"],
        "ready_for_future_controlled_reevaluation_prep": ready,
        "new_owner_readiness_score_generated": False,
        "new_owner_readiness_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": _dedupe([*register["warnings"], *completeness["warnings"]]),
    }


def _reevaluation_readiness_precheck(as_of_date: str, result: dict[str, Any]) -> dict[str, Any]:
    criteria = {
        "target_evidence_day_count_passed": result["controlled_reevaluation_day_count_passed"],
        "research_output_completeness_passed": result["research_output_completeness_passed"],
        "controlled_reevaluation_coverage_passed": result["controlled_reevaluation_coverage_passed"],
        "owner_readiness_gate_not_run": True,
        "controlled_reevaluation_not_executed": True,
        "new_gate_score_not_generated": True,
        "new_gate_decision_not_generated": True,
    }
    ready = all(criteria.values())
    return {
        "precheck_id": "A-SHARE-REEVALUATION-READINESS-PRECHECK-AFTER-BACKFILL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "precheck_status": "ready" if ready else "not_ready",
        "criteria": criteria,
        "ready_for_future_controlled_reevaluation_prep": ready,
        "owner_readiness_gate_executed": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "blocking_reasons": [],
        "warnings": [] if ready else ["precheck_not_ready_after_backfill"],
    }


def _go_no_go_after_backfill(as_of_date: str, result: dict[str, Any], precheck: dict[str, Any]) -> dict[str, Any]:
    ready = bool(precheck["ready_for_future_controlled_reevaluation_prep"])
    decision = "go_for_future_controlled_reevaluation_prep" if ready else "no_go_additional_evidence_required"
    recommended = RECOMMENDED_NEXT_VERSION_IF_READY if ready else RECOMMENDED_NEXT_VERSION
    failed = [key for key, value in precheck["criteria"].items() if not value]
    return {
        "decision_id": "A-SHARE-GO-NO-GO-AFTER-HISTORICAL-BACKFILL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "decision_type": "future_controlled_reevaluation_prep_decision",
        "not_owner_readiness_gate_decision": True,
        "owner_readiness_gate_executed": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "decision": decision,
        "rationale": [
            f"eligible_day_count={result['eligible_day_count']}",
            f"target_total_evidence_days={result['target_total_evidence_days']}",
            f"blocker_coverage_ratio={result['blocker_coverage_ratio']}",
            f"precheck_status={precheck['precheck_status']}",
        ],
        "failed_criteria": failed,
        "blocking_reasons": [],
        "warnings": [] if ready else ["additional_evidence_required_after_backfill"],
        "recommended_next_version": recommended,
    }


def _remaining_gap_register_after_backfill(as_of_date: str, result: dict[str, Any], precheck: dict[str, Any], go_no_go: dict[str, Any]) -> dict[str, Any]:
    gaps = []
    if not result["controlled_reevaluation_day_count_passed"]:
        gaps.append({"gap_id": "GAP001", "description": "Eligible evidence day count remains below target.", "blocking": True})
    if not result["controlled_reevaluation_coverage_passed"]:
        gaps.append({"gap_id": "GAP002", "description": "Blocker coverage remains below controlled reevaluation threshold.", "blocking": True})
    if precheck["precheck_status"] != "ready":
        gaps.append({"gap_id": "GAP003", "description": "Future controlled reevaluation prep precheck is not ready.", "blocking": True})
    return {
        "register_id": "A-SHARE-REMAINING-GAP-REGISTER-AFTER-BACKFILL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "go_no_go_decision": go_no_go["decision"],
        "gaps": gaps,
        "remaining_gap_count": len(gaps),
        "blocking_gap_count": sum(1 for gap in gaps if gap["blocking"]),
    }


def _reevaluation_readiness_boundary_check(as_of_date: str, backfill: dict[str, Any], protected_untouched: bool) -> dict[str, Any]:
    blocking = [] if protected_untouched else ["protected_paths_modified"]
    return {
        "boundary_id": "A-SHARE-REEVALUATION-READINESS-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "public_network_refresh_run": backfill["public_network_refresh_run"],
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
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
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "protected_paths_untouched": protected_untouched,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _reevaluation_readiness_closeout_result(as_of_date: str, result: dict[str, Any], precheck: dict[str, Any], go_no_go: dict[str, Any], gaps: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-REEVALUATION-READINESS-CLOSEOUT-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "eligible_day_count": result["eligible_day_count"],
        "target_total_evidence_days": result["target_total_evidence_days"],
        "precheck_status": precheck["precheck_status"],
        "go_no_go_decision": go_no_go["decision"],
        "remaining_gap_count": gaps["remaining_gap_count"],
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "overall_passed": bool(boundary["overall_passed"]),
        "blocking_reasons": list(boundary["blocking_reasons"]),
        "warnings": _dedupe([*result["warnings"], *precheck["warnings"], *go_no_go["warnings"]]),
        "recommended_next_version": go_no_go["recommended_next_version"],
    }


def _post_close_refresh_plan(as_of_date: str) -> dict[str, Any]:
    return {
        "plan_id": "A-SHARE-POST-CLOSE-REFRESH-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "timezone": "Asia/Shanghai",
        "recommended_run_time": "15:45",
        "run_days": "A-share trading days only",
        "refresh_scope": ["trading_calendar_check", "public_market_data_refresh", "data_freshness_result", "owner_daily_status_update"],
        "explicitly_excluded_scope": ["broker", "real_account", "orders", "order_preview", "buy_sell_signals", "owner_readiness_gate", "controlled_reevaluation", "live_trading"],
        "public_market_data_only": True,
        "requires_trading_day_check_before_run": True,
        "safe_to_schedule_as_reminder": True,
        "safe_to_schedule_as_automatic_local_job": False,
        "reason_automatic_local_job_not_enabled": "Do not silently install OS scheduler or daemon from this version.",
    }


def _post_close_refresh_command_plan(as_of_date: str) -> dict[str, Any]:
    return {
        "command_plan_id": "A-SHARE-POST-CLOSE-REFRESH-COMMAND-PLAN",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "manual_commands": [
            "python -m trading_core.cli refresh-a-share-data-freshness --target-as-of-date <YYYY-MM-DD>",
            "python -m trading_core.cli owner-daily-status --as-of-date <YYYY-MM-DD>",
        ],
        "optional_research_pipeline_command_after_data_refresh": [
            "python -m trading_core.cli rerun-a-share-research-pipeline-from-refreshed-data --as-of-date <YYYY-MM-DD>"
        ],
        "forbidden_commands": ["python -m trading_core.cli run-daily", "broker commands", "order preview commands", "owner-readiness gate commands"],
        "commands_executed_by_this_version": [],
    }


def _post_close_refresh_safety_boundary(as_of_date: str, plan: dict[str, Any]) -> dict[str, Any]:
    excluded = set(plan["explicitly_excluded_scope"])
    blocking = []
    for item in ["broker", "real_account", "orders", "order_preview", "buy_sell_signals", "owner_readiness_gate", "controlled_reevaluation", "live_trading"]:
        if item not in excluded:
            blocking.append(f"excluded_scope_missing:{item}")
    return {
        "boundary_id": "A-SHARE-POST-CLOSE-REFRESH-SAFETY-BOUNDARY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "public_market_data_only": True,
        "installs_scheduler": False,
        "installs_daemon": False,
        "modifies_startup_tasks": False,
        "safe_to_schedule_as_automatic_local_job": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_executed": False,
        "live_trading_ready": False,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _post_close_refresh_schedule_recommendation(as_of_date: str, plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "schedule_id": "A-SHARE-POST-CLOSE-REFRESH-SCHEDULE-RECOMMENDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "timezone": plan["timezone"],
        "recommended_run_time": plan["recommended_run_time"],
        "run_days": plan["run_days"],
        "recommendation_type": "manual_reminder_or_documented_instruction_only",
        "installs_scheduler": False,
        "installs_windows_task_scheduler_entry": False,
        "installs_cron_entry": False,
        "installs_daemon": False,
        "safe_to_schedule_as_reminder": True,
        "safe_to_schedule_as_automatic_local_job": False,
    }


def _day_completeness(paths: ProjectPaths, day: str) -> dict[str, bool]:
    return {
        "features": (paths.data_dir / "equity_features" / "daily" / day / "feature_manifest.json").exists(),
        "research_scores": (paths.data_dir / "equity_scores" / "daily" / day / "score_manifest.json").exists(),
        "research_candidates": (paths.data_dir / "equity_selection" / "daily" / day / "candidate_manifest.json").exists(),
        "virtual_only_portfolio_research": (paths.data_dir / "equity_portfolios" / "daily" / day / "portfolio_manifest.json").exists(),
        "research_briefing": (paths.data_dir / "equity_briefings" / "daily" / day / "briefing_manifest.json").exists(),
        "source_trace": (paths.data_dir / "equity_briefings" / "daily" / day / "briefing_source_trace.json").exists(),
        "boundary_check": (paths.data_dir / "equity_briefings" / "daily" / day / "briefing_boundary_check.json").exists(),
        "manifest": all(
            [
                (paths.data_dir / "equity_features" / "daily" / day / "feature_manifest.json").exists(),
                (paths.data_dir / "equity_scores" / "daily" / day / "score_manifest.json").exists(),
                (paths.data_dir / "equity_selection" / "daily" / day / "candidate_manifest.json").exists(),
                (paths.data_dir / "equity_portfolios" / "daily" / day / "portfolio_manifest.json").exists(),
                (paths.data_dir / "equity_briefings" / "daily" / day / "briefing_manifest.json").exists(),
            ]
        ),
    }


def _scorecard_category(category: str, passed: bool, strength: str) -> dict[str, Any]:
    return {"category": category, "status": "passed" if passed else "not_ready", "evidence_strength": strength}


def _date_count(frame: pd.DataFrame, day: str) -> int:
    if frame.empty or "date" not in frame.columns:
        return 0
    dates = frame["date"].astype(str).str[:10]
    return int((dates == day).sum())


def _historical_backfill_manifest(paths: ProjectPaths, as_of_date: str, request: dict[str, Any], discovery: dict[str, Any], availability: dict[str, Any], plan: dict[str, Any], result: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = _artifact_paths(paths, as_of_date)
    return _manifest("A-SHARE-HISTORICAL-BACKFILL-MANIFEST", paths, as_of_date, ["historical_backfill_request", "historical_trading_day_discovery", "historical_source_data_availability", "historical_backfill_execution_plan", "historical_research_backfill_result", "historical_backfill_boundary_check"], artifact_paths, result["overall_passed"] and boundary["overall_passed"], [*result["blocking_reasons"], *boundary["blocking_reasons"]])


def _recomputed_evidence_manifest(paths: ProjectPaths, as_of_date: str, request: dict[str, Any], register: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = _artifact_paths(paths, as_of_date)
    return _manifest("A-SHARE-RECOMPUTED-EVIDENCE-MANIFEST", paths, as_of_date, ["recomputed_evidence_request", "recomputed_evidence_eligible_day_register", "recomputed_research_output_completeness_matrix", "recomputed_evidence_quality_scorecard", "recomputed_blocker_evidence_mapping", "recomputed_evidence_result"], artifact_paths, result["overall_passed"], result["blocking_reasons"])


def _reevaluation_readiness_manifest(paths: ProjectPaths, as_of_date: str, precheck: dict[str, Any], go_no_go: dict[str, Any], gaps: dict[str, Any], result: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    artifact_paths = _artifact_paths(paths, as_of_date)
    return _manifest("A-SHARE-REEVALUATION-READINESS-MANIFEST", paths, as_of_date, ["reevaluation_readiness_precheck", "go_no_go_after_backfill", "remaining_gap_register_after_backfill", "reevaluation_readiness_closeout_result", "reevaluation_readiness_boundary_check"], artifact_paths, result["overall_passed"], result["blocking_reasons"])


def _manifest(manifest_id: str, paths: ProjectPaths, as_of_date: str, keys: list[str], artifact_paths: dict[str, Path], overall_passed: bool, blocking: list[str]) -> dict[str, Any]:
    output_artifacts = {key: _rel(artifact_paths[key], paths.project_root) for key in keys if key in artifact_paths}
    return {
        "manifest_id": manifest_id,
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "source_version": SOURCE_VERSION,
        "output_artifacts": output_artifacts,
        "artifact_hashes": {key: _sha256(artifact_paths[key]) for key in keys if key in artifact_paths and artifact_paths[key].exists()},
        "overall_passed": overall_passed,
        "blocking_reasons": blocking,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    historical_data = paths.data_dir / "equity_historical_research_backfill" / "daily" / as_of_date
    historical_output = paths.outputs_dir / "equity_historical_research_backfill" / "daily" / as_of_date
    evidence_data = paths.data_dir / "equity_research_evidence_recomputed" / "daily" / as_of_date
    evidence_output = paths.outputs_dir / "equity_research_evidence_recomputed" / "daily" / as_of_date
    closeout_data = paths.data_dir / "equity_reevaluation_readiness_closeout" / "daily" / as_of_date
    closeout_output = paths.outputs_dir / "equity_reevaluation_readiness_closeout" / "daily" / as_of_date
    refresh_data = paths.data_dir / "equity_post_close_refresh_planning" / "daily" / as_of_date
    refresh_output = paths.outputs_dir / "equity_post_close_refresh_planning" / "daily" / as_of_date
    return {
        "historical_backfill_request": historical_data / "historical_backfill_request.json",
        "historical_trading_day_discovery": historical_data / "historical_trading_day_discovery.json",
        "historical_source_data_availability": historical_data / "historical_source_data_availability.json",
        "historical_backfill_execution_plan": historical_data / "historical_backfill_execution_plan.json",
        "historical_research_backfill_result": historical_data / "historical_research_backfill_result.json",
        "historical_backfill_boundary_check": historical_data / "historical_backfill_boundary_check.json",
        "historical_backfill_manifest": historical_data / "historical_backfill_manifest.json",
        "historical_report": historical_output / "A_SHARE_HISTORICAL_RESEARCH_BACKFILL_RESULT.md",
        "recomputed_evidence_request": evidence_data / "recomputed_evidence_request.json",
        "recomputed_evidence_eligible_day_register": evidence_data / "recomputed_evidence_eligible_day_register.json",
        "recomputed_research_output_completeness_matrix": evidence_data / "recomputed_research_output_completeness_matrix.json",
        "recomputed_evidence_quality_scorecard": evidence_data / "recomputed_evidence_quality_scorecard.json",
        "recomputed_blocker_evidence_mapping": evidence_data / "recomputed_blocker_evidence_mapping.json",
        "recomputed_evidence_result": evidence_data / "recomputed_evidence_result.json",
        "recomputed_evidence_manifest": evidence_data / "recomputed_evidence_manifest.json",
        "recomputed_report": evidence_output / "A_SHARE_RECOMPUTED_EVIDENCE_REVIEW.md",
        "reevaluation_readiness_precheck": closeout_data / "reevaluation_readiness_precheck.json",
        "go_no_go_after_backfill": closeout_data / "go_no_go_after_backfill.json",
        "remaining_gap_register_after_backfill": closeout_data / "remaining_gap_register_after_backfill.json",
        "reevaluation_readiness_closeout_result": closeout_data / "reevaluation_readiness_closeout_result.json",
        "reevaluation_readiness_boundary_check": closeout_data / "reevaluation_readiness_boundary_check.json",
        "reevaluation_readiness_manifest": closeout_data / "reevaluation_readiness_manifest.json",
        "readiness_report": closeout_output / "A_SHARE_REEVALUATION_READINESS_AFTER_BACKFILL.md",
        "post_close_refresh_plan": refresh_data / "post_close_refresh_plan.json",
        "post_close_refresh_command_plan": refresh_data / "post_close_refresh_command_plan.json",
        "post_close_refresh_safety_boundary": refresh_data / "post_close_refresh_safety_boundary.json",
        "post_close_refresh_schedule_recommendation": refresh_data / "post_close_refresh_schedule_recommendation.json",
        "refresh_plan_report": refresh_output / "A_SHARE_POST_CLOSE_REFRESH_PLAN.md",
    }


def _ensure_dirs(paths: ProjectPaths, as_of_date: str) -> None:
    for path in _artifact_paths(paths, as_of_date).values():
        path.parent.mkdir(parents=True, exist_ok=True)


def _historical_markdown(discovery: dict[str, Any], result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Historical Research Backfill Result",
            "",
            f"- resolved_trading_days: {discovery['resolved_trading_days']}",
            f"- selected_backfill_days: {result['selected_backfill_days']}",
            f"- backfilled_days: {result['backfilled_days']}",
            f"- failed_backfill_days: {result['failed_backfill_days']}",
            f"- eligible_day_count_after_backfill: {result['eligible_day_count_after_backfill']}",
            f"- target_total_evidence_days_passed: {result['target_total_evidence_days_passed']}",
            "",
            "Research-only historical backfill records shortfall honestly. It is not a trade instruction.",
            "",
        ]
    )


def _recomputed_markdown(result: dict[str, Any], scorecard: dict[str, Any], blocker_mapping: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Recomputed Evidence Review",
            "",
            f"- eligible_day_count: {result['eligible_day_count']}",
            f"- evidence_quality_overall_status: {result['evidence_quality_overall_status']}",
            f"- blocker_coverage_ratio: {result['blocker_coverage_ratio']}",
            f"- ready_for_future_controlled_reevaluation_prep: {result['ready_for_future_controlled_reevaluation_prep']}",
            "",
            "Research scores are not trade signals. Research candidates are not buy/sell signals.",
            "Virtual-only portfolio outputs are not real account portfolios.",
            "",
        ]
    )


def _readiness_markdown(precheck: dict[str, Any], go_no_go: dict[str, Any], result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Reevaluation Readiness After Backfill",
            "",
            f"- precheck_status: {precheck['precheck_status']}",
            f"- decision: {go_no_go['decision']}",
            f"- owner_readiness_gate_rerun: {result['owner_readiness_gate_rerun']}",
            f"- controlled_reevaluation_executed: {result['controlled_reevaluation_executed']}",
            "- known_owner_readiness_state: blocked",
            "- source_readiness_score: 54 / threshold: 75 / gap: 21",
            "",
        ]
    )


def _refresh_markdown(plan: dict[str, Any], command_plan: dict[str, Any], boundary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Post-Close Refresh Plan",
            "",
            f"- timezone: {plan['timezone']}",
            f"- recommended_run_time: {plan['recommended_run_time']}",
            f"- public_market_data_only: {plan['public_market_data_only']}",
            f"- installs_scheduler: {boundary['installs_scheduler']}",
            "",
            "## Manual Commands",
            *[f"- `{item}`" for item in command_plan["manual_commands"]],
            "",
            "This plan does not install cron, Windows Task Scheduler, startup tasks, or a daemon.",
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


def _dedupe(values: list[str]) -> list[str]:
    return list(dict.fromkeys(str(value) for value in values if value))


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
