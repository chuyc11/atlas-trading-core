"""Build the v0.9.5 research evidence accumulation and reevaluation prep package."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from trading_core.equity_data_quality.common import read_frame, read_json, utc_now, write_json
from trading_core.storage.file_paths import ProjectPaths, project_paths

TARGET_VERSION = "v0.9.5-a-share-research-evidence-accumulation-quality-review-and-reevaluation-prep"
SOURCE_RESEARCH_VERSION = "v0.9.4-a-share-research-pipeline-rerun-from-refreshed-data"
SOURCE_FRESHNESS_VERSION = "v0.9.3-a-share-data-freshness-refresh"
RECOMMENDED_NEXT_VERSION = "v0.9.6-a-share-controlled-readiness-reevaluation-or-final-not-ready-closeout"
DEFAULT_AS_OF_DATE = "2026-07-01"
BASELINE_OWNER_READINESS_DATE = "2026-06-26"
SOURCE_READINESS_SCORE = 54
MINIMUM_OWNER_READINESS_SCORE = 75
MINIMUM_EVIDENCE_DAYS_FOR_PREP = 2
MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION = 5
MINIMUM_STRONG_OR_MODERATE_EVIDENCE_ITEMS_FOR_PREP = 3
MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_PREP = 0.6
MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION = 0.85

REQUIRED_OUTPUT_CLASSES = [
    "source_data_freshness",
    "features",
    "research_scores",
    "research_candidates",
    "virtual_only_portfolio_research",
    "research_briefing",
    "source_trace",
    "boundary_check",
    "manifest",
]


def build_a_share_research_evidence_accumulation_and_prep(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    phase_a_dir = _phase_a_dir(paths, as_of_date)
    phase_a_output_dir = _phase_a_output_dir(paths, as_of_date)
    phase_b_dir = _phase_b_dir(paths, as_of_date)
    phase_b_output_dir = _phase_b_output_dir(paths, as_of_date)
    for directory in [phase_a_dir, phase_a_output_dir, phase_b_dir, phase_b_output_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    protected_before = _protected_snapshot(paths)
    request = _evidence_accumulation_request(as_of_date)
    source_inventory = _source_artifact_inventory(paths, as_of_date)
    completeness = _research_output_completeness_matrix(paths, as_of_date, source_inventory)
    eligible_register = _evidence_eligible_day_register(as_of_date, completeness)
    consistency = _research_output_consistency_diagnostics(paths, as_of_date, eligible_register)
    candidate_diagnostics = _candidate_overlap_and_turnover_diagnostics(paths, as_of_date, eligible_register)
    score_diagnostics = _score_distribution_diagnostics(paths, as_of_date, eligible_register)
    portfolio_diagnostics = _virtual_portfolio_research_diagnostics(paths, as_of_date, eligible_register)
    briefing_diagnostics = _research_briefing_quality_diagnostics(paths, as_of_date, eligible_register)
    protected_after_phase_a = _protected_snapshot(paths)
    boundary_validation = _research_only_boundary_validation(
        paths=paths,
        as_of_date=as_of_date,
        protected_untouched=protected_before == protected_after_phase_a,
        diagnostics=[candidate_diagnostics, score_diagnostics, portfolio_diagnostics, briefing_diagnostics],
    )
    readiness_gap = _readiness_evidence_gap_analysis(paths, as_of_date, eligible_register, boundary_validation)
    evidence_result = _evidence_accumulation_result(
        as_of_date=as_of_date,
        register=eligible_register,
        completeness=completeness,
        consistency=consistency,
        candidate_diagnostics=candidate_diagnostics,
        score_diagnostics=score_diagnostics,
        portfolio_diagnostics=portfolio_diagnostics,
        briefing_diagnostics=briefing_diagnostics,
        boundary_validation=boundary_validation,
        readiness_gap=readiness_gap,
    )
    phase_a_paths = _phase_a_artifact_paths(paths, as_of_date)
    phase_a_manifest = _evidence_accumulation_manifest(paths, as_of_date, phase_a_paths, evidence_result)
    _write_payloads(
        {
            "evidence_accumulation_request": request,
            "source_artifact_inventory": source_inventory,
            "evidence_eligible_day_register": eligible_register,
            "research_output_completeness_matrix": completeness,
            "research_output_consistency_diagnostics": consistency,
            "candidate_overlap_and_turnover_diagnostics": candidate_diagnostics,
            "score_distribution_diagnostics": score_diagnostics,
            "virtual_portfolio_research_diagnostics": portfolio_diagnostics,
            "research_briefing_quality_diagnostics": briefing_diagnostics,
            "research_only_boundary_validation": boundary_validation,
            "readiness_evidence_gap_analysis": readiness_gap,
            "evidence_accumulation_result": evidence_result,
            "evidence_accumulation_manifest": phase_a_manifest,
        },
        phase_a_paths,
    )
    _write_text(phase_a_paths["evidence_report"], _evidence_markdown(evidence_result, eligible_register, completeness, consistency, candidate_diagnostics))
    _write_text(phase_a_paths["gap_report"], _gap_markdown(readiness_gap, boundary_validation))

    quality_request = _evidence_quality_review_request(as_of_date)
    scorecard = _evidence_quality_scorecard(paths, as_of_date, eligible_register, completeness, consistency, boundary_validation)
    blocker_mapping = _blocker_evidence_mapping(paths, as_of_date, eligible_register, readiness_gap)
    input_package = _reevaluation_input_candidate_package(as_of_date, eligible_register, scorecard, blocker_mapping, readiness_gap, boundary_validation)
    precheck = _controlled_reevaluation_precheck(as_of_date, eligible_register, blocker_mapping, boundary_validation)
    go_no_go = _go_no_go_for_future_reevaluation(as_of_date, eligible_register, scorecard, blocker_mapping, precheck)
    not_ready = _not_ready_reason_register(as_of_date, go_no_go, eligible_register, blocker_mapping, precheck)
    protected_after_phase_b = _protected_snapshot(paths)
    prep_boundary = _reevaluation_prep_boundary_check(
        as_of_date=as_of_date,
        protected_untouched=protected_before == protected_after_phase_b,
        go_no_go=go_no_go,
    )
    prep_result = _reevaluation_prep_result(as_of_date, scorecard, blocker_mapping, input_package, precheck, go_no_go, not_ready, prep_boundary)
    phase_b_paths = _phase_b_artifact_paths(paths, as_of_date)
    prep_manifest = _reevaluation_prep_manifest(paths, as_of_date, phase_b_paths, prep_result)
    _write_payloads(
        {
            "evidence_quality_review_request": quality_request,
            "evidence_quality_scorecard": scorecard,
            "blocker_evidence_mapping": blocker_mapping,
            "reevaluation_input_candidate_package": input_package,
            "controlled_reevaluation_precheck": precheck,
            "go_no_go_for_future_reevaluation": go_no_go,
            "not_ready_reason_register": not_ready,
            "reevaluation_prep_boundary_check": prep_boundary,
            "reevaluation_prep_result": prep_result,
            "reevaluation_prep_manifest": prep_manifest,
        },
        phase_b_paths,
    )
    _write_text(phase_b_paths["quality_review_report"], _quality_markdown(scorecard, blocker_mapping, readiness_gap, prep_result))
    _write_text(phase_b_paths["prep_package_report"], _prep_markdown(input_package, precheck, not_ready))
    _write_text(phase_b_paths["go_no_go_report"], _go_no_go_markdown(go_no_go, precheck))

    return {
        "builder_id": "A-SHARE-RESEARCH-EVIDENCE-ACCUMULATION-AND-PREP",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": bool(evidence_result["overall_passed"] and prep_result["overall_passed"]),
        "blocking_reasons": [*evidence_result["blocking_reasons"], *prep_result["blocking_reasons"]],
        "warnings": [*evidence_result["warnings"], *prep_result["warnings"]],
        "eligible_day_count": eligible_register["eligible_day_count"],
        "eligible_days": [day["date"] for day in eligible_register["eligible_days"]],
        "ineligible_days": [day["date"] for day in eligible_register["ineligible_days"]],
        "evidence_accumulation_status": evidence_result["evidence_accumulation_status"],
        "evidence_quality_overall_status": scorecard["evidence_quality_overall_status"],
        "blocker_coverage_ratio": blocker_mapping["blocker_coverage_ratio"],
        "precheck_status": precheck["precheck_status"],
        "future_reevaluation_decision": go_no_go["decision"],
        "ready_for_future_controlled_reevaluation_prep": go_no_go["ready_for_future_controlled_reevaluation_prep"],
        "controlled_reevaluation_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "build_from_existing_data_run": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "research_output_used_as_trade_instruction": False,
        "reevaluation_prep_used_as_trade_instruction": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "phase_a_artifacts": {key: _rel(path, paths.project_root) for key, path in phase_a_paths.items()},
        "phase_b_artifacts": {key: _rel(path, paths.project_root) for key, path in phase_b_paths.items()},
    }


def _evidence_accumulation_request(as_of_date: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-EVIDENCE-ACCUMULATION-REQUEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "baseline_owner_readiness_date": BASELINE_OWNER_READINESS_DATE,
        "refreshed_research_output_date": as_of_date,
        "source_versions": {
            "data_freshness": SOURCE_FRESHNESS_VERSION,
            "research_pipeline_rerun": SOURCE_RESEARCH_VERSION,
        },
        "scope": [
            "multi_day_research_output_evidence",
            "research_output_completeness",
            "candidate_overlap_and_turnover",
            "score_distribution_diagnostics",
            "virtual_only_portfolio_diagnostics",
            "briefing_quality_diagnostics",
            "readiness_evidence_gap_analysis",
        ],
        "allow_data_refresh": False,
        "allow_research_pipeline_rerun": False,
        "allow_owner_readiness_gate": False,
        "allow_controlled_reevaluation_execution": False,
        "allow_new_gate_score": False,
        "allow_new_gate_decision": False,
        "allow_broker": False,
        "allow_order_preview": False,
        "research_only": True,
        "virtual_only": True,
        "not_investment_advice": True,
    }


def _source_artifact_inventory(paths: ProjectPaths, as_of_date: str) -> dict[str, Any]:
    candidates = sorted(_candidate_dates(paths, as_of_date))
    source_paths = [
        paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_refresh_result.json",
        paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_coverage_summary.json",
        paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date / "research_pipeline_rerun_result.json",
        paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date / "research_pipeline_boundary_check.json",
        paths.data_dir / "equity_owner_closeout_review" / "daily" / BASELINE_OWNER_READINESS_DATE / "unresolved_blocker_register.json",
        paths.data_dir / "equity_owner_v090_rc" / "daily" / BASELINE_OWNER_READINESS_DATE / "v090_audit_sweep_result.json",
        paths.data_dir / "equity_owner_v090_rc" / "daily" / BASELINE_OWNER_READINESS_DATE / "v090_full_pytest_result.json",
    ]
    for date in candidates:
        source_paths.extend(_day_artifact_paths(paths, date).values())
    artifacts = [_artifact_record(path, paths.project_root) for path in sorted(set(source_paths), key=lambda item: item.as_posix())]
    return {
        "inventory_id": "A-SHARE-RESEARCH-EVIDENCE-SOURCE-ARTIFACT-INVENTORY",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "candidate_dates": candidates,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "v093_data_freshness_present": (paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_refresh_result.json").exists(),
        "v094_research_pipeline_rerun_present": (paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date / "research_pipeline_rerun_result.json").exists(),
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "blocking_reasons": [],
        "warnings": [],
    }


def _research_output_completeness_matrix(paths: ProjectPaths, as_of_date: str, inventory: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for date in inventory["candidate_dates"]:
        artifacts = _day_artifact_paths(paths, date)
        source_data_freshness = date == as_of_date and (paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_refresh_result.json").exists()
        values = {
            "source_data_freshness": source_data_freshness,
            "features": artifacts["feature_manifest"].exists(),
            "research_scores": artifacts["score_manifest"].exists(),
            "research_candidates": artifacts["candidate_manifest"].exists(),
            "virtual_only_portfolio_research": artifacts["portfolio_manifest"].exists(),
            "research_briefing": artifacts["briefing_manifest"].exists(),
            "source_trace": artifacts["briefing_source_trace"].exists(),
            "boundary_check": artifacts["briefing_boundary_check"].exists(),
            "manifest": all(artifacts[name].exists() for name in ["feature_manifest", "score_manifest", "candidate_manifest", "portfolio_manifest", "briefing_manifest"]),
        }
        rows.append(
            {
                "date": date,
                "source_data_date": _source_data_date(paths, date, as_of_date),
                **{f"{key}_present": value for key, value in values.items()},
                "complete_for_evidence": all(value for key, value in values.items() if key != "source_data_freshness"),
                "complete_for_refreshed_source_evidence": all(values.values()),
                "missing_output_classes": [key for key, value in values.items() if not value],
            }
        )
    return {
        "matrix_id": "A-SHARE-RESEARCH-OUTPUT-COMPLETENESS-MATRIX",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "required_output_classes": REQUIRED_OUTPUT_CLASSES,
        "rows": rows,
        "research_output_completeness_passed": any(row["complete_for_evidence"] for row in rows),
        "all_candidate_days_complete": all(row["complete_for_evidence"] for row in rows) if rows else False,
        "blocking_reasons": [],
        "warnings": ["source_data_freshness_available_only_for_refreshed_research_output_date"] if any(not row["source_data_freshness_present"] for row in rows) else [],
    }


def _evidence_eligible_day_register(as_of_date: str, completeness: dict[str, Any]) -> dict[str, Any]:
    eligible_days = []
    ineligible_days = []
    for row in completeness["rows"]:
        blocking = []
        if not row["complete_for_evidence"]:
            blocking.extend(row["missing_output_classes"])
        item = {
            "date": row["date"],
            "source_data_date": row["source_data_date"],
            "features_present": row["features_present"],
            "scores_present": row["research_scores_present"],
            "candidates_present": row["research_candidates_present"],
            "virtual_portfolio_present": row["virtual_only_portfolio_research_present"],
            "briefing_present": row["research_briefing_present"],
            "source_trace_present": row["source_trace_present"],
            "boundary_validation_present": row["boundary_check_present"],
            "research_only_marking_present": row["boundary_check_present"],
            "eligible_for_prep": not blocking,
            "eligible_for_future_controlled_reevaluation": False,
            "eligibility_warnings": [] if row["source_data_freshness_present"] else ["source_data_freshness_artifact_not_available_for_historical_day"],
            "eligibility_blocking_reasons": blocking,
        }
        if item["eligible_for_prep"]:
            eligible_days.append(item)
        else:
            ineligible_days.append(item)
    eligible_count = len(eligible_days)
    prep_passed = eligible_count >= MINIMUM_EVIDENCE_DAYS_FOR_PREP
    controlled_passed = eligible_count >= MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION
    return {
        "register_id": "A-SHARE-EVIDENCE-ELIGIBLE-DAY-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "minimum_evidence_days_for_prep": MINIMUM_EVIDENCE_DAYS_FOR_PREP,
        "minimum_evidence_days_for_future_controlled_reevaluation": MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION,
        "eligible_day_count": eligible_count,
        "eligible_days": eligible_days,
        "ineligible_days": ineligible_days,
        "planned_but_not_evidence_days": [],
        "prep_evidence_day_count_passed": prep_passed,
        "controlled_reevaluation_day_count_passed": controlled_passed,
        "overall_day_eligibility_status": "sufficient_for_prep" if prep_passed else "insufficient",
    }


def _research_output_consistency_diagnostics(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    days = [item["date"] for item in register["eligible_days"]]
    counts = []
    for date in days:
        counts.append(
            {
                "date": date,
                "strict_tradable_count": _json_number(paths.data_dir / "equity_selection" / "daily" / date / "candidate_generation_summary.json", ["strict_tradable_count"]),
                "scored_symbols": _json_number(paths.data_dir / "equity_selection" / "daily" / date / "candidate_generation_summary.json", ["scored_symbols"]),
                "long_candidate_count": _candidate_count(paths, date, "long_candidates"),
                "mid_candidate_count": _candidate_count(paths, date, "mid_candidates"),
                "short_candidate_count": _candidate_count(paths, date, "short_candidates"),
            }
        )
    status = "insufficient" if len(days) < MINIMUM_EVIDENCE_DAYS_FOR_PREP else "partial"
    if len(days) >= MINIMUM_EVIDENCE_DAYS_FOR_PREP and all(row["long_candidate_count"] for row in counts):
        status = "sufficient_for_prep_not_for_controlled_reevaluation"
    return {
        "diagnostics_id": "A-SHARE-RESEARCH-OUTPUT-CONSISTENCY-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "eligible_day_count": len(days),
        "minimum_evidence_days_for_prep": MINIMUM_EVIDENCE_DAYS_FOR_PREP,
        "minimum_evidence_days_for_future_controlled_reevaluation": MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION,
        "research_output_consistency_status": status,
        "daily_counts": counts,
        "cross_day_consistency_supported": len(days) >= MINIMUM_EVIDENCE_DAYS_FOR_PREP,
        "controlled_reevaluation_consistency_supported": len(days) >= MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION,
        "blocking_reasons": [],
        "warnings": [] if len(days) >= MINIMUM_EVIDENCE_DAYS_FOR_PREP else ["insufficient_eligible_days_for_cross_day_consistency"],
    }


def _candidate_overlap_and_turnover_diagnostics(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    days = [item["date"] for item in register["eligible_days"]]
    sets_by_day = {date: _candidate_symbols(paths, date) for date in days}
    comparisons = []
    for previous, current in zip(days, days[1:]):
        previous_set = sets_by_day[previous]
        current_set = sets_by_day[current]
        stable = sorted(previous_set & current_set)
        added = sorted(current_set - previous_set)
        removed = sorted(previous_set - current_set)
        comparisons.append(
            {
                "previous_date": previous,
                "current_date": current,
                "stable_research_candidate_count": len(stable),
                "added_to_research_candidate_set_count": len(added),
                "removed_from_research_candidate_set_count": len(removed),
                "stable_research_candidate": stable[:25],
                "added_to_research_candidate_set": added[:25],
                "removed_from_research_candidate_set": removed[:25],
                "turnover_ratio": round((len(added) + len(removed)) / max(len(previous_set | current_set), 1), 6),
            }
        )
    status = "insufficient" if len(days) < 2 else "partial"
    return {
        "diagnostics_id": "A-SHARE-CANDIDATE-OVERLAP-AND-TURNOVER-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "research_only": True,
        "not_order_instruction": True,
        "candidate_label_policy": [
            "added_to_research_candidate_set",
            "removed_from_research_candidate_set",
            "stable_research_candidate",
        ],
        "candidate_stability_status": status,
        "eligible_day_count": len(days),
        "comparisons": comparisons,
        "forbidden_wording_present": _contains_any(json.dumps(comparisons, ensure_ascii=False).lower(), ["buy", "sell", "entry", "exit", "trade", "recommendation"]),
        "blocking_reasons": [],
        "warnings": [] if comparisons else ["insufficient_eligible_days_for_candidate_overlap"],
    }


def _score_distribution_diagnostics(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    days = [item["date"] for item in register["eligible_days"]]
    distributions = []
    for date in days:
        payload = read_json(paths.data_dir / "equity_scores" / "daily" / date / "score_distribution.json")
        scores = payload.get("scores", {})
        distributions.append(
            {
                "date": date,
                "score_count": int(next(iter(scores.values()), {}).get("count") or 0) if scores else 0,
                "score_columns": sorted(scores.keys()),
                "long_score_mean": _nested_number(scores, ["LongScore", "mean"]),
                "mid_score_mean": _nested_number(scores, ["MidScore", "mean"]),
                "short_score_mean": _nested_number(scores, ["ShortScore", "mean"]),
            }
        )
    status = "insufficient" if not distributions else ("partial" if len(distributions) < MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION else "sufficient")
    return {
        "diagnostics_id": "A-SHARE-SCORE-DISTRIBUTION-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "score_distribution_status": status,
        "not_trade_signal": True,
        "not_owner_readiness_score": True,
        "score_boundary_statements": [
            "research_score != buy/sell signal",
            "research_score != owner-readiness score",
        ],
        "distributions": distributions,
        "blocking_reasons": [],
        "warnings": [] if distributions else ["missing_score_distribution_evidence"],
    }


def _virtual_portfolio_research_diagnostics(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    days = [item["date"] for item in register["eligible_days"]]
    rows = []
    for date in days:
        summary = read_json(paths.data_dir / "equity_portfolios" / "daily" / date / "portfolio_weight_summary.json")
        rows.append({"date": date, "weight_summary": summary})
    return {
        "diagnostics_id": "A-SHARE-VIRTUAL-PORTFOLIO-RESEARCH-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "virtual_portfolio_research_status": "partial" if rows else "insufficient",
        "virtual_only": True,
        "not_real_portfolio": True,
        "not_order_instruction": True,
        "boundary_statements": [
            "virtual portfolio is virtual-only",
            "not real portfolio",
            "not order instruction",
        ],
        "daily_portfolio_summaries": rows,
        "blocking_reasons": [],
        "warnings": [] if rows else ["missing_virtual_portfolio_research_evidence"],
    }


def _research_briefing_quality_diagnostics(paths: ProjectPaths, as_of_date: str, register: dict[str, Any]) -> dict[str, Any]:
    days = [item["date"] for item in register["eligible_days"]]
    rows = []
    forbidden = ["strong buy", "must buy", "guaranteed profit", "live trading ready", "order instruction: true"]
    for date in days:
        path = paths.outputs_dir / "equity_briefings" / "daily" / date / "DAILY_STOCK_SELECTION_BRIEFING.md"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        lower = text.lower()
        rows.append(
            {
                "date": date,
                "briefing_present": bool(text),
                "not_investment_advice_wording_present": "not investment advice" in lower or "不是投资建议" in text,
                "forbidden_wording_hits": [word for word in forbidden if word in lower],
            }
        )
    passed = all(not row["forbidden_wording_hits"] for row in rows) if rows else False
    return {
        "diagnostics_id": "A-SHARE-RESEARCH-BRIEFING-QUALITY-DIAGNOSTICS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "briefing_quality_status": "passed" if passed else "partial",
        "not_investment_advice": True,
        "not_order_instruction": True,
        "briefing_boundary_statement": "research briefing is not investment advice",
        "daily_briefing_checks": rows,
        "blocking_reasons": [],
        "warnings": [],
    }


def _research_only_boundary_validation(
    *,
    paths: ProjectPaths,
    as_of_date: str,
    protected_untouched: bool,
    diagnostics: list[dict[str, Any]],
) -> dict[str, Any]:
    forbidden_present = any(diagnostic.get("forbidden_wording_present") for diagnostic in diagnostics)
    blocking = []
    if not protected_untouched:
        blocking.append("protected_order_trade_account_paths_modified")
    if forbidden_present:
        blocking.append("forbidden_research_candidate_wording_present")
    v094 = read_json(paths.data_dir / "equity_research_pipeline_rerun" / "daily" / as_of_date / "research_pipeline_rerun_result.json")
    return {
        "validation_id": "A-SHARE-RESEARCH-ONLY-BOUNDARY-VALIDATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_v094_result_passed": bool(v094.get("overall_passed")),
        "research_only_boundary_validation_passed": not blocking,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "build_from_existing_data_run": False,
        "owner_daily_pack_run": False,
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
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
        "research_output_used_as_trade_instruction": False,
        "protected_order_trade_account_paths_untouched": protected_untouched,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _readiness_evidence_gap_analysis(paths: ProjectPaths, as_of_date: str, register: dict[str, Any], boundary: dict[str, Any]) -> dict[str, Any]:
    blockers = _source_blockers(paths)
    evidence_days = register["eligible_day_count"]
    gaps = []
    if evidence_days < MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION:
        gaps.append(
            {
                "gap_id": "G001",
                "category": "insufficient_evidence_days",
                "description": "Eligible research evidence days do not meet future controlled reevaluation threshold.",
                "required": MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION,
                "actual": evidence_days,
                "blocking": True,
            }
        )
    if not boundary["research_only_boundary_validation_passed"]:
        gaps.append({"gap_id": "G002", "category": "boundary_integrity", "description": "Research-only boundary validation failed.", "blocking": True})
    return {
        "analysis_id": "A-SHARE-READINESS-EVIDENCE-GAP-ANALYSIS",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "source_blocker_count": len(blockers),
        "evidence_supported_gap_count": 0,
        "remaining_gap_count": len(gaps),
        "remaining_gaps": gaps,
        "readiness_evidence_gap_analysis_completed": True,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "blocking_reasons": [],
        "warnings": [],
    }


def _evidence_accumulation_result(
    *,
    as_of_date: str,
    register: dict[str, Any],
    completeness: dict[str, Any],
    consistency: dict[str, Any],
    candidate_diagnostics: dict[str, Any],
    score_diagnostics: dict[str, Any],
    portfolio_diagnostics: dict[str, Any],
    briefing_diagnostics: dict[str, Any],
    boundary_validation: dict[str, Any],
    readiness_gap: dict[str, Any],
) -> dict[str, Any]:
    blocking = list(boundary_validation["blocking_reasons"])
    evidence_status = "sufficient_for_prep" if register["prep_evidence_day_count_passed"] else "partial"
    return {
        "result_id": "A-SHARE-EVIDENCE-ACCUMULATION-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [*completeness["warnings"], *consistency["warnings"], *candidate_diagnostics["warnings"], *score_diagnostics["warnings"], *portfolio_diagnostics["warnings"], *briefing_diagnostics["warnings"]],
        "eligible_day_count": register["eligible_day_count"],
        "eligible_days": [day["date"] for day in register["eligible_days"]],
        "ineligible_days": [day["date"] for day in register["ineligible_days"]],
        "prep_evidence_day_count_passed": register["prep_evidence_day_count_passed"],
        "controlled_reevaluation_day_count_passed": register["controlled_reevaluation_day_count_passed"],
        "research_output_completeness_passed": completeness["research_output_completeness_passed"],
        "research_output_consistency_status": consistency["research_output_consistency_status"],
        "candidate_stability_status": candidate_diagnostics["candidate_stability_status"],
        "score_distribution_status": score_diagnostics["score_distribution_status"],
        "virtual_portfolio_research_status": portfolio_diagnostics["virtual_portfolio_research_status"],
        "briefing_quality_status": briefing_diagnostics["briefing_quality_status"],
        "research_only_boundary_validation_passed": boundary_validation["research_only_boundary_validation_passed"],
        "readiness_evidence_gap_analysis_completed": readiness_gap["readiness_evidence_gap_analysis_completed"],
        "evidence_accumulation_status": evidence_status,
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "build_from_existing_data_run": False,
        "owner_readiness_gate_rerun": False,
        "controlled_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _evidence_quality_review_request(as_of_date: str) -> dict[str, Any]:
    return {
        "request_id": "A-SHARE-EVIDENCE-QUALITY-REVIEW-REQUEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_evidence_accumulation_result_path": f"data/equity_research_evidence_accumulation/daily/{as_of_date}/evidence_accumulation_result.json",
        "source_readiness_evidence_gap_analysis_path": f"data/equity_research_evidence_accumulation/daily/{as_of_date}/readiness_evidence_gap_analysis.json",
        "review_scope": [
            "evidence_strength_classification",
            "blocker_evidence_mapping",
            "reevaluation_input_candidate_package",
            "controlled_reevaluation_precheck",
            "go_no_go_for_future_reevaluation",
            "not_ready_reason_register",
        ],
        "allow_controlled_reevaluation_execution": False,
        "allow_new_gate_score": False,
        "allow_new_gate_decision": False,
        "allow_threshold_change": False,
        "allow_waiver": False,
        "research_only": True,
        "not_owner_readiness_decision": True,
    }


def _evidence_quality_scorecard(
    paths: ProjectPaths,
    as_of_date: str,
    register: dict[str, Any],
    completeness: dict[str, Any],
    consistency: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    source_trace_partial = any(row["source_trace_present"] for row in completeness["rows"])
    categories = [
        _scorecard_category(
            "multi_day_output_completeness",
            "passed" if register["prep_evidence_day_count_passed"] else "insufficient",
            "moderate" if register["prep_evidence_day_count_passed"] else "weak",
            [f"data/equity_research_evidence_accumulation/daily/{as_of_date}/research_output_completeness_matrix.json"],
            [] if register["prep_evidence_day_count_passed"] else ["minimum_prep_evidence_days_not_met"],
            [],
        ),
        _scorecard_category(
            "research_output_consistency",
            "partial" if consistency["cross_day_consistency_supported"] else "insufficient",
            "moderate" if consistency["cross_day_consistency_supported"] else "weak",
            [f"data/equity_research_evidence_accumulation/daily/{as_of_date}/research_output_consistency_diagnostics.json"],
            [] if consistency["cross_day_consistency_supported"] else ["insufficient_cross_day_observations"],
            [],
        ),
        _scorecard_category(
            "boundary_integrity",
            "passed" if boundary["research_only_boundary_validation_passed"] else "failed",
            "strong" if boundary["research_only_boundary_validation_passed"] else "missing",
            [f"data/equity_research_evidence_accumulation/daily/{as_of_date}/research_only_boundary_validation.json"],
            boundary["blocking_reasons"],
            [],
        ),
        _scorecard_category(
            "source_traceability",
            "partial" if source_trace_partial else "insufficient",
            "moderate" if source_trace_partial else "weak",
            [f"data/equity_research_evidence_accumulation/daily/{as_of_date}/source_artifact_inventory.json"],
            [],
            ["source_data_freshness_artifact_only_available_for_refreshed_date"],
        ),
        _scorecard_category(
            "operator_usability",
            "passed",
            "moderate",
            [f"data/equity_owner_v090_rc/daily/{BASELINE_OWNER_READINESS_DATE}/v090_audit_sweep_result.json"],
            [],
            [],
        ),
    ]
    counts = _evidence_strength_counts(categories)
    strong_or_moderate = counts["strong"] + counts["moderate"]
    overall = "insufficient" if strong_or_moderate < MINIMUM_STRONG_OR_MODERATE_EVIDENCE_ITEMS_FOR_PREP else "partial"
    return {
        "scorecard_id": "A-SHARE-EVIDENCE-QUALITY-SCORECARD",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "not_owner_readiness_score": True,
        "not_gate_score": True,
        "evidence_quality_overall_status": overall,
        "categories": categories,
        "strong_evidence_count": counts["strong"],
        "moderate_evidence_count": counts["moderate"],
        "weak_evidence_count": counts["weak"],
        "missing_evidence_count": counts["missing"],
        "blocking_reasons": [],
        "warnings": [] if overall != "insufficient" else ["evidence_quality_not_sufficient_for_controlled_reevaluation"],
    }


def _blocker_evidence_mapping(paths: ProjectPaths, as_of_date: str, register: dict[str, Any], readiness_gap: dict[str, Any]) -> dict[str, Any]:
    source_blockers = [blocker for blocker in _source_blockers(paths) if blocker.get("blocks_owner_readiness_acceptance", True)]
    blockers = []
    eligible_days = register["eligible_day_count"]
    for blocker in source_blockers:
        strength = "missing"
        support = []
        missing = ["five_eligible_research_output_days", "controlled_reevaluation_specific_evidence"]
        if blocker.get("category") in {"missing_recovery_evidence", "missing_audit_verified_evidence", "insufficient_history_if_present"} and eligible_days >= MINIMUM_EVIDENCE_DAYS_FOR_PREP:
            strength = "moderate"
            support = [f"data/equity_research_evidence_accumulation/daily/{as_of_date}/evidence_eligible_day_register.json"]
            missing = ["five_eligible_research_output_days", "future_controlled_reevaluation_evidence"]
        elif blocker.get("category") in {"v090_rc_known_blocked_state"}:
            strength = "weak"
            support = [f"data/equity_owner_closeout_review/daily/{BASELINE_OWNER_READINESS_DATE}/unresolved_blocker_register.json"]
        blockers.append(
            {
                "blocker_id": blocker.get("blocker_id", ""),
                "source_version": blocker.get("source_version", ""),
                "description": blocker.get("description", ""),
                "blocks_owner_readiness": bool(blocker.get("blocks_owner_readiness_acceptance", True)),
                "current_status": "open",
                "evidence_strength": strength,
                "supporting_evidence_items": support,
                "missing_evidence": missing,
                "can_support_future_prep": strength in {"strong", "moderate"},
                "can_support_controlled_reevaluation": False,
                "requires_additional_days": True,
                "requires_manual_review": False,
                "notes": "Evidence is prep-only and does not execute a gate.",
            }
        )
    counts = _blocker_strength_counts(blockers)
    covered = counts["strong"] + counts["moderate"]
    ratio = round(covered / len(blockers), 6) if blockers else 0.0
    return {
        "mapping_id": "A-SHARE-BLOCKER-EVIDENCE-MAPPING",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "source_owner_readiness_state": "blocked",
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "blockers": blockers,
        "blocker_count": len(blockers),
        "blockers_with_strong_evidence": counts["strong"],
        "blockers_with_moderate_evidence": counts["moderate"],
        "blockers_with_weak_evidence": counts["weak"],
        "blockers_with_missing_evidence": counts["missing"],
        "blocker_coverage_ratio": ratio,
        "minimum_blocker_coverage_ratio_for_prep": MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_PREP,
        "minimum_blocker_coverage_ratio_for_controlled_reevaluation": MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION,
        "prep_coverage_passed": ratio >= MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_PREP,
        "controlled_reevaluation_coverage_passed": ratio >= MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION,
        "blocking_reasons": [],
        "warnings": ["blocker_coverage_below_controlled_reevaluation_threshold"] if ratio < MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION else [],
    }


def _reevaluation_input_candidate_package(
    as_of_date: str,
    register: dict[str, Any],
    scorecard: dict[str, Any],
    blocker_mapping: dict[str, Any],
    readiness_gap: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    missing = []
    if not register["controlled_reevaluation_day_count_passed"]:
        missing.append("minimum_evidence_days_for_future_controlled_reevaluation")
    if not blocker_mapping["controlled_reevaluation_coverage_passed"]:
        missing.append("blocker_coverage_ratio_for_controlled_reevaluation")
    if scorecard["evidence_quality_overall_status"] != "sufficient":
        missing.append("sufficient_evidence_quality_status")
    return {
        "package_id": "A-SHARE-REEVALUATION-INPUT-CANDIDATE-PACKAGE",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "package_status": "ready" if not missing else "not_ready",
        "not_gate_execution": True,
        "owner_readiness_gate_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "candidate_input_sections": {
            "source_versions": {"data_freshness": SOURCE_FRESHNESS_VERSION, "research_pipeline_rerun": SOURCE_RESEARCH_VERSION},
            "eligible_days": register["eligible_days"],
            "evidence_items": scorecard["categories"],
            "blocker_mapping": {"blocker_count": blocker_mapping["blocker_count"], "blocker_coverage_ratio": blocker_mapping["blocker_coverage_ratio"]},
            "boundary_validation": boundary,
            "remaining_gaps": readiness_gap["remaining_gaps"],
        },
        "missing_required_sections": missing,
        "blocking_reasons": [],
        "warnings": ["candidate_package_not_ready_for_gate_execution"] if missing else [],
    }


def _controlled_reevaluation_precheck(
    as_of_date: str,
    register: dict[str, Any],
    blocker_mapping: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    criteria = [
        {
            "criterion": "minimum_evidence_days_for_controlled_reevaluation",
            "required": MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION,
            "actual": register["eligible_day_count"],
            "passed": register["controlled_reevaluation_day_count_passed"],
            "blocking": True,
        },
        {
            "criterion": "blocker_coverage_ratio_for_controlled_reevaluation",
            "required": MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION,
            "actual": blocker_mapping["blocker_coverage_ratio"],
            "passed": blocker_mapping["controlled_reevaluation_coverage_passed"],
            "blocking": True,
        },
        {
            "criterion": "research_only_boundary_validation",
            "required": True,
            "actual": boundary["research_only_boundary_validation_passed"],
            "passed": boundary["research_only_boundary_validation_passed"],
            "blocking": True,
        },
    ]
    passed = all(criterion["passed"] for criterion in criteria)
    return {
        "precheck_id": "A-SHARE-CONTROLLED-REEVALUATION-PRECHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "controlled_reevaluation_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "precheck_status": "ready" if passed else "not_ready",
        "criteria": criteria,
        "blocking_reasons": [],
        "warnings": [] if passed else ["controlled_reevaluation_precheck_not_ready"],
    }


def _go_no_go_for_future_reevaluation(
    as_of_date: str,
    register: dict[str, Any],
    scorecard: dict[str, Any],
    blocker_mapping: dict[str, Any],
    precheck: dict[str, Any],
) -> dict[str, Any]:
    ready = precheck["precheck_status"] == "ready" and scorecard["evidence_quality_overall_status"] == "sufficient"
    decision = "go_for_future_controlled_reevaluation_prep" if ready else "no_go_additional_evidence_required"
    failed = [criterion["criterion"] for criterion in precheck["criteria"] if not criterion["passed"]]
    return {
        "decision_id": "A-SHARE-GO-NO-GO-FOR-FUTURE-REEVALUATION",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "decision_type": "future_reevaluation_prep_decision",
        "not_owner_readiness_gate_decision": True,
        "controlled_reevaluation_executed": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "decision": decision,
        "ready_for_future_controlled_reevaluation_prep": ready,
        "allowed_next_step": "controlled_reevaluation_prep_review" if ready else "additional_evidence_accumulation_or_not_ready_closeout",
        "forbidden_next_step": "execute_controlled_reevaluation_now",
        "go_criteria": ["minimum_5_eligible_days", "blocker_coverage_ratio_at_least_0.85", "research_only_boundary_validation"],
        "failed_criteria": failed,
        "rationale": [
            f"eligible_day_count={register['eligible_day_count']}",
            f"blocker_coverage_ratio={blocker_mapping['blocker_coverage_ratio']}",
            f"evidence_quality_overall_status={scorecard['evidence_quality_overall_status']}",
            "This is not an owner-readiness gate decision.",
        ],
        "blocking_reasons": [],
        "warnings": ["additional_evidence_required_before_controlled_reevaluation"] if not ready else [],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _not_ready_reason_register(
    as_of_date: str,
    go_no_go: dict[str, Any],
    register: dict[str, Any],
    blocker_mapping: dict[str, Any],
    precheck: dict[str, Any],
) -> dict[str, Any]:
    reasons = []
    if register["eligible_day_count"] < MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION:
        reasons.append(
            {
                "reason_id": "NR001",
                "category": "insufficient_evidence_days",
                "description": "Eligible research evidence days are below future controlled reevaluation threshold.",
                "blocking": True,
                "required_to_resolve": f"collect at least {MINIMUM_EVIDENCE_DAYS_FOR_FUTURE_CONTROLLED_REEVALUATION} eligible research evidence days",
                "evidence_needed": ["additional_daily_research_output_packages", "source_trace_and_boundary_validation_for_each_day"],
                "can_be_resolved_without_gate": True,
                "requires_future_version": True,
            }
        )
    if blocker_mapping["blocker_coverage_ratio"] < MINIMUM_BLOCKER_COVERAGE_RATIO_FOR_CONTROLLED_REEVALUATION:
        reasons.append(
            {
                "reason_id": "NR002",
                "category": "insufficient_blocker_coverage",
                "description": "Blocker evidence coverage is below controlled reevaluation threshold.",
                "blocking": True,
                "required_to_resolve": "raise blocker evidence coverage to at least 0.85",
                "evidence_needed": ["audit_verified_blocker_evidence_mapping", "manual_review_if_needed"],
                "can_be_resolved_without_gate": True,
                "requires_future_version": True,
            }
        )
    return {
        "register_id": "A-SHARE-NOT-READY-REASON-REGISTER",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "not_ready": not go_no_go["ready_for_future_controlled_reevaluation_prep"],
        "reasons": reasons,
        "reason_count": len(reasons),
        "minimum_reasons_expected_if_no_go": 1,
        "owner_readiness_state_preserved": "blocked",
        "owner_operationally_acceptable": False,
        "precheck_status": precheck["precheck_status"],
    }


def _reevaluation_prep_boundary_check(*, as_of_date: str, protected_untouched: bool, go_no_go: dict[str, Any]) -> dict[str, Any]:
    blocking = [] if protected_untouched else ["protected_order_trade_account_paths_modified"]
    return {
        "boundary_id": "A-SHARE-REEVALUATION-PREP-BOUNDARY-CHECK",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "evidence_quality_review_only": True,
        "reevaluation_prep_only": True,
        "controlled_reevaluation_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "threshold_lowered": False,
        "auto_waiver_allowed": False,
        "manual_waiver_approval_recorded": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "data_refresh_run": False,
        "research_pipeline_rerun_run": False,
        "build_from_existing_data_run": False,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "day2_executed": False,
        "live_trading_ready": False,
        "reevaluation_prep_used_as_trade_instruction": False,
        "future_reevaluation_decision": go_no_go["decision"],
        "protected_order_trade_account_paths_untouched": protected_untouched,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [],
    }


def _reevaluation_prep_result(
    as_of_date: str,
    scorecard: dict[str, Any],
    blocker_mapping: dict[str, Any],
    input_package: dict[str, Any],
    precheck: dict[str, Any],
    go_no_go: dict[str, Any],
    not_ready: dict[str, Any],
    boundary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "result_id": "A-SHARE-REEVALUATION-PREP-RESULT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": boundary["overall_passed"],
        "blocking_reasons": list(boundary["blocking_reasons"]),
        "warnings": [*scorecard["warnings"], *blocker_mapping["warnings"], *input_package["warnings"], *precheck["warnings"], *go_no_go["warnings"]],
        "evidence_quality_review_completed": True,
        "blocker_evidence_mapping_completed": True,
        "reevaluation_input_candidate_package_generated": True,
        "controlled_reevaluation_precheck_completed": True,
        "go_no_go_decision_generated": True,
        "not_ready_reason_register_generated": True,
        "evidence_quality_overall_status": scorecard["evidence_quality_overall_status"],
        "strong_evidence_count": scorecard["strong_evidence_count"],
        "moderate_evidence_count": scorecard["moderate_evidence_count"],
        "weak_evidence_count": scorecard["weak_evidence_count"],
        "missing_evidence_count": scorecard["missing_evidence_count"],
        "blocker_count": blocker_mapping["blocker_count"],
        "blocker_coverage_ratio": blocker_mapping["blocker_coverage_ratio"],
        "prep_coverage_passed": blocker_mapping["prep_coverage_passed"],
        "controlled_reevaluation_coverage_passed": blocker_mapping["controlled_reevaluation_coverage_passed"],
        "reevaluation_input_candidate_package_status": input_package["package_status"],
        "precheck_status": precheck["precheck_status"],
        "controlled_reevaluation_precheck_status": precheck["precheck_status"],
        "future_reevaluation_decision": go_no_go["decision"],
        "not_ready_reason_count": not_ready["reason_count"],
        "ready_for_future_controlled_reevaluation_prep": go_no_go["ready_for_future_controlled_reevaluation_prep"],
        "controlled_reevaluation_executed": False,
        "owner_readiness_gate_rerun": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "known_owner_readiness_state": "blocked",
        "owner_operationally_acceptable": False,
        "source_readiness_score": SOURCE_READINESS_SCORE,
        "minimum_owner_readiness_score": MINIMUM_OWNER_READINESS_SCORE,
        "score_gap": MINIMUM_OWNER_READINESS_SCORE - SOURCE_READINESS_SCORE,
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _evidence_accumulation_manifest(paths: ProjectPaths, as_of_date: str, artifact_paths: dict[str, Path], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-EVIDENCE-ACCUMULATION-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "phase": "evidence_accumulation",
        "artifact_paths": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _reevaluation_prep_manifest(paths: ProjectPaths, as_of_date: str, artifact_paths: dict[str, Path], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "manifest_id": "A-SHARE-REEVALUATION-PREP-MANIFEST",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "generated_at": utc_now(),
        "phase": "evidence_quality_review_and_reevaluation_prep",
        "artifact_paths": {key: _rel(path, paths.project_root) for key, path in artifact_paths.items()},
        "overall_passed": result["overall_passed"],
        "blocking_reasons": result["blocking_reasons"],
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
    }


def _phase_a_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = _phase_a_dir(paths, as_of_date)
    output_dir = _phase_a_output_dir(paths, as_of_date)
    return {
        "evidence_accumulation_request": data_dir / "evidence_accumulation_request.json",
        "source_artifact_inventory": data_dir / "source_artifact_inventory.json",
        "evidence_eligible_day_register": data_dir / "evidence_eligible_day_register.json",
        "research_output_completeness_matrix": data_dir / "research_output_completeness_matrix.json",
        "research_output_consistency_diagnostics": data_dir / "research_output_consistency_diagnostics.json",
        "candidate_overlap_and_turnover_diagnostics": data_dir / "candidate_overlap_and_turnover_diagnostics.json",
        "score_distribution_diagnostics": data_dir / "score_distribution_diagnostics.json",
        "virtual_portfolio_research_diagnostics": data_dir / "virtual_portfolio_research_diagnostics.json",
        "research_briefing_quality_diagnostics": data_dir / "research_briefing_quality_diagnostics.json",
        "research_only_boundary_validation": data_dir / "research_only_boundary_validation.json",
        "readiness_evidence_gap_analysis": data_dir / "readiness_evidence_gap_analysis.json",
        "evidence_accumulation_result": data_dir / "evidence_accumulation_result.json",
        "evidence_accumulation_manifest": data_dir / "evidence_accumulation_manifest.json",
        "evidence_report": output_dir / "A_SHARE_MULTI_DAY_RESEARCH_EVIDENCE_ACCUMULATION.md",
        "gap_report": output_dir / "A_SHARE_READINESS_EVIDENCE_GAP_ANALYSIS.md",
    }


def _phase_b_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = _phase_b_dir(paths, as_of_date)
    output_dir = _phase_b_output_dir(paths, as_of_date)
    return {
        "evidence_quality_review_request": data_dir / "evidence_quality_review_request.json",
        "evidence_quality_scorecard": data_dir / "evidence_quality_scorecard.json",
        "blocker_evidence_mapping": data_dir / "blocker_evidence_mapping.json",
        "reevaluation_input_candidate_package": data_dir / "reevaluation_input_candidate_package.json",
        "controlled_reevaluation_precheck": data_dir / "controlled_reevaluation_precheck.json",
        "go_no_go_for_future_reevaluation": data_dir / "go_no_go_for_future_reevaluation.json",
        "not_ready_reason_register": data_dir / "not_ready_reason_register.json",
        "reevaluation_prep_boundary_check": data_dir / "reevaluation_prep_boundary_check.json",
        "reevaluation_prep_result": data_dir / "reevaluation_prep_result.json",
        "reevaluation_prep_manifest": data_dir / "reevaluation_prep_manifest.json",
        "quality_review_report": output_dir / "A_SHARE_READINESS_EVIDENCE_QUALITY_REVIEW.md",
        "prep_package_report": output_dir / "A_SHARE_CONTROLLED_REEVALUATION_PREP_PACKAGE.md",
        "go_no_go_report": output_dir / "A_SHARE_GO_NO_GO_FOR_FUTURE_REEVALUATION.md",
    }


def _evidence_markdown(result: dict[str, Any], register: dict[str, Any], completeness: dict[str, Any], consistency: dict[str, Any], candidate_diagnostics: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Multi-Day Research Evidence Accumulation",
            "",
            "## 1. Evidence Summary",
            f"- evidence_accumulation_status: {result['evidence_accumulation_status']}",
            f"- eligible_day_count: {result['eligible_day_count']}",
            "",
            "## 2. Source Artifact Inventory",
            "- Source artifacts are read-only local files.",
            "",
            "## 3. Evidence-Eligible Days",
            f"- eligible_days: {result['eligible_days']}",
            f"- ineligible_days: {result['ineligible_days']}",
            "",
            "## 4. Output Completeness Matrix",
            f"- research_output_completeness_passed: {result['research_output_completeness_passed']}",
            f"- required_output_classes: {completeness['required_output_classes']}",
            "",
            "## 5. Cross-Day Consistency",
            f"- research_output_consistency_status: {consistency['research_output_consistency_status']}",
            "",
            "## 6. Candidate Overlap and Turnover",
            f"- candidate_stability_status: {candidate_diagnostics['candidate_stability_status']}",
            "- Labels used: added_to_research_candidate_set, removed_from_research_candidate_set, stable_research_candidate.",
            "",
            "## 7. Score Distribution Diagnostics",
            "- research_score != buy/sell signal",
            "- research_score != owner-readiness score",
            "",
            "## 8. Virtual-Only Portfolio Diagnostics",
            "- virtual portfolio is virtual-only",
            "- not real portfolio",
            "- not order instruction",
            "",
            "## 9. Briefing Quality Diagnostics",
            "- Briefings are research-only and not investment advice.",
            "",
            "## 10. Boundary Validation",
            f"- research_only_boundary_validation_passed: {result['research_only_boundary_validation_passed']}",
            "",
            "## 11. Evidence Status and Next Step",
            f"- recommended_next_version: {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )


def _gap_markdown(gap: dict[str, Any], boundary: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Readiness Evidence Gap Analysis",
            "",
            "## 1. Gap Summary",
            f"- remaining_gap_count: {gap['remaining_gap_count']}",
            "",
            "## 2. Source Owner-Readiness State",
            "- known_owner_readiness_state: blocked",
            "- owner_operationally_acceptable: false",
            "- readiness_score: 54 / threshold: 75 / gap: 21",
            "",
            "## 3. Evidence-Supported Blockers",
            f"- evidence_supported_gap_count: {gap['evidence_supported_gap_count']}",
            "",
            "## 4. Remaining Blocking Gaps",
            *[f"- {item['gap_id']}: {item['description']}" for item in gap["remaining_gaps"]],
            "",
            "## 5. Boundary Preservation",
            f"- research_only_boundary_validation_passed: {boundary['research_only_boundary_validation_passed']}",
            "- No new owner-readiness score or decision is generated.",
            "",
            "## 6. Why This Is Not a Gate Decision",
            "- This is not an owner-readiness gate decision.",
            "- This does not execute controlled reevaluation.",
            "- Blocked remains blocked.",
            "",
            "## 7. Recommended Next Step",
            f"- {RECOMMENDED_NEXT_VERSION}",
            "",
        ]
    )


def _quality_markdown(scorecard: dict[str, Any], blocker_mapping: dict[str, Any], gap: dict[str, Any], result: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Readiness Evidence Quality Review",
            "",
            "## 1. Review Summary",
            f"- evidence_quality_overall_status: {scorecard['evidence_quality_overall_status']}",
            "",
            "## 2. Source Evidence Package",
            "- Source package comes from v0.9.5 Phase A evidence accumulation.",
            "",
            "## 3. Evidence Quality Scorecard",
            f"- strong: {scorecard['strong_evidence_count']}",
            f"- moderate: {scorecard['moderate_evidence_count']}",
            f"- weak: {scorecard['weak_evidence_count']}",
            f"- missing: {scorecard['missing_evidence_count']}",
            "",
            "## 4. Evidence Strength by Category",
            *[f"- {item['category']}: {item['status']} / {item['evidence_strength']}" for item in scorecard["categories"]],
            "",
            "## 5. Blocker Coverage",
            f"- blocker_coverage_ratio: {blocker_mapping['blocker_coverage_ratio']}",
            "",
            "## 6. Strong / Moderate / Weak / Missing Evidence",
            f"- blockers_with_moderate_evidence: {blocker_mapping['blockers_with_moderate_evidence']}",
            f"- blockers_with_missing_evidence: {blocker_mapping['blockers_with_missing_evidence']}",
            "",
            "## 7. Remaining Evidence Gaps",
            *[f"- {item['category']}: {item['description']}" for item in gap["remaining_gaps"]],
            "",
            "## 8. Boundary Preservation",
            "- controlled_reevaluation_executed=false",
            "- new_gate_score_generated=false",
            "- new_gate_decision_generated=false",
            "",
            "## 9. Why This Is Not a Gate Score",
            "- Evidence quality status is not an owner-readiness score.",
            "- This is not an owner-readiness gate decision.",
            "",
            "## 10. Recommended Next Step",
            f"- {result['recommended_next_version']}",
            "",
        ]
    )


def _prep_markdown(input_package: dict[str, Any], precheck: dict[str, Any], not_ready: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Controlled Reevaluation Prep Package",
            "",
            "## 1. Prep Package Summary",
            f"- package_status: {input_package['package_status']}",
            "",
            "## 2. Candidate Inputs",
            f"- missing_required_sections: {input_package['missing_required_sections']}",
            "",
            "## 3. Eligible Evidence Days",
            f"- eligible_days: {[day['date'] for day in input_package['candidate_input_sections']['eligible_days']]}",
            "",
            "## 4. Evidence Items",
            f"- evidence_items: {len(input_package['candidate_input_sections']['evidence_items'])}",
            "",
            "## 5. Blocker Mapping",
            f"- blocker_mapping: {input_package['candidate_input_sections']['blocker_mapping']}",
            "",
            "## 6. Missing Required Inputs",
            *[f"- {item}" for item in input_package["missing_required_sections"]],
            "",
            "## 7. Controlled Reevaluation Precheck",
            f"- precheck_status: {precheck['precheck_status']}",
            "",
            "## 8. Why Reevaluation Is Not Executed Here",
            "- This does not execute controlled reevaluation.",
            "- This does not generate a new readiness score.",
            "- Blocked remains blocked.",
            "",
            "## 9. Required Future Conditions",
            *[f"- {reason['required_to_resolve']}" for reason in not_ready["reasons"]],
            "",
        ]
    )


def _go_no_go_markdown(go_no_go: dict[str, Any], precheck: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# A-Share Go / No-Go for Future Reevaluation",
            "",
            "## 1. Go / No-Go Decision",
            f"- decision: {go_no_go['decision']}",
            "",
            "## 2. Decision Type",
            f"- decision_type: {go_no_go['decision_type']}",
            "",
            "## 3. Explicit Non-Gate Nature",
            "This is not an owner-readiness gate decision.",
            "This does not execute controlled reevaluation.",
            "This does not generate a new readiness score.",
            "Blocked remains blocked.",
            "No trading action is authorized.",
            "",
            "## 4. Go Criteria",
            *[f"- {item}" for item in go_no_go["go_criteria"]],
            "",
            "## 5. Failed Criteria",
            *[f"- {item}" for item in go_no_go["failed_criteria"]],
            "",
            "## 6. Blocking Reasons",
            f"- precheck_status: {precheck['precheck_status']}",
            "",
            "## 7. Allowed Next Step",
            f"- {go_no_go['allowed_next_step']}",
            "",
            "## 8. Forbidden Next Step",
            f"- {go_no_go['forbidden_next_step']}",
            "",
            "## 9. Recommended Next Version",
            f"- {go_no_go['recommended_next_version']}",
            "",
        ]
    )


def _candidate_dates(paths: ProjectPaths, as_of_date: str) -> set[str]:
    roots = [
        paths.data_dir / "equity_features" / "daily",
        paths.data_dir / "equity_scores" / "daily",
        paths.data_dir / "equity_selection" / "daily",
        paths.data_dir / "equity_portfolios" / "daily",
        paths.data_dir / "equity_briefings" / "daily",
    ]
    dates = {as_of_date}
    for root in roots:
        if root.exists():
            dates.update(path.name for path in root.iterdir() if path.is_dir() and path.name <= as_of_date and path.name.startswith("2026-"))
    return dates


def _day_artifact_paths(paths: ProjectPaths, date: str) -> dict[str, Path]:
    return {
        "feature_manifest": paths.data_dir / "equity_features" / "daily" / date / "feature_manifest.json",
        "feature_summary": paths.data_dir / "equity_features" / "daily" / date / "feature_generation_summary.json",
        "score_manifest": paths.data_dir / "equity_scores" / "daily" / date / "score_manifest.json",
        "score_distribution": paths.data_dir / "equity_scores" / "daily" / date / "score_distribution.json",
        "candidate_manifest": paths.data_dir / "equity_selection" / "daily" / date / "candidate_manifest.json",
        "candidate_summary": paths.data_dir / "equity_selection" / "daily" / date / "candidate_generation_summary.json",
        "portfolio_manifest": paths.data_dir / "equity_portfolios" / "daily" / date / "portfolio_manifest.json",
        "portfolio_weight_summary": paths.data_dir / "equity_portfolios" / "daily" / date / "portfolio_weight_summary.json",
        "briefing_manifest": paths.data_dir / "equity_briefings" / "daily" / date / "briefing_manifest.json",
        "briefing_source_trace": paths.data_dir / "equity_briefings" / "daily" / date / "briefing_source_trace.json",
        "briefing_boundary_check": paths.data_dir / "equity_briefings" / "daily" / date / "briefing_boundary_check.json",
    }


def _source_data_date(paths: ProjectPaths, date: str, as_of_date: str) -> str:
    if date == as_of_date:
        refresh = read_json(paths.data_dir / "equity_data_freshness" / "daily" / as_of_date / "data_freshness_refresh_result.json")
        return str(refresh.get("resolved_actual_data_date") or date)
    return date


def _candidate_symbols(paths: ProjectPaths, date: str) -> set[str]:
    result: set[str] = set()
    for name in ["long_candidates", "mid_candidates", "short_candidates"]:
        path = paths.data_dir / "equity_selection" / "daily" / date / f"{name}.json"
        rows = _read_json_list(path)
        if not rows:
            frame = read_frame(paths.data_dir / "equity_selection" / "daily" / date / f"{name}.parquet")
            rows = frame.to_dict(orient="records") if not frame.empty else []
        result.update(str(row.get("symbol") or row.get("ts_code") or "") for row in rows if row.get("symbol") or row.get("ts_code"))
    return {symbol for symbol in result if symbol}


def _candidate_count(paths: ProjectPaths, date: str, name: str) -> int:
    path = paths.data_dir / "equity_selection" / "daily" / date / f"{name}.json"
    rows = _read_json_list(path)
    if rows:
        return len(rows)
    frame = read_frame(paths.data_dir / "equity_selection" / "daily" / date / f"{name}.parquet")
    return 0 if frame.empty else len(frame)


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        for key in ["rows", "candidates", "items"]:
            if isinstance(data.get(key), list):
                return [item for item in data[key] if isinstance(item, dict)]
    return []


def _json_number(path: Path, keys: list[str]) -> float | int | None:
    payload: Any = read_json(path)
    for key in keys:
        if not isinstance(payload, dict):
            return None
        payload = payload.get(key)
    return payload if isinstance(payload, (int, float)) else None


def _nested_number(payload: dict[str, Any], keys: list[str]) -> float | int | None:
    value: Any = payload
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value if isinstance(value, (int, float)) else None


def _source_blockers(paths: ProjectPaths) -> list[dict[str, Any]]:
    payload = read_json(paths.data_dir / "equity_owner_closeout_review" / "daily" / BASELINE_OWNER_READINESS_DATE / "unresolved_blocker_register.json")
    blockers = payload.get("blockers", [])
    return [blocker for blocker in blockers if isinstance(blocker, dict)]


def _scorecard_category(category: str, status: str, evidence_strength: str, supporting_artifacts: list[str], blocking_gaps: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "category": category,
        "status": status,
        "evidence_strength": evidence_strength,
        "supporting_artifacts": supporting_artifacts,
        "blocking_gaps": blocking_gaps,
        "warnings": warnings,
    }


def _evidence_strength_counts(categories: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "strong": sum(1 for item in categories if item["evidence_strength"] == "strong"),
        "moderate": sum(1 for item in categories if item["evidence_strength"] == "moderate"),
        "weak": sum(1 for item in categories if item["evidence_strength"] == "weak"),
        "missing": sum(1 for item in categories if item["evidence_strength"] == "missing"),
    }


def _blocker_strength_counts(blockers: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "strong": sum(1 for item in blockers if item["evidence_strength"] == "strong"),
        "moderate": sum(1 for item in blockers if item["evidence_strength"] == "moderate"),
        "weak": sum(1 for item in blockers if item["evidence_strength"] == "weak"),
        "missing": sum(1 for item in blockers if item["evidence_strength"] == "missing"),
    }


def _artifact_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": _rel(path, root),
        "exists": path.exists(),
        "sha256": _sha256(path),
        "size_bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
    }


def _sha256(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def _protected_snapshot(paths: ProjectPaths) -> dict[str, str]:
    roots = [
        paths.data_dir / "orders",
        paths.data_dir / "trades",
        paths.data_dir / "accounts",
        paths.outputs_dir / "orders",
        paths.outputs_dir / "trades",
        paths.outputs_dir / "accounts",
    ]
    result = {}
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                result[_rel(path, paths.project_root)] = _sha256(path) or ""
    return result


def _write_payloads(payloads: dict[str, dict[str, Any]], paths: dict[str, Path]) -> None:
    for key, payload in payloads.items():
        write_json(paths[key], payload)


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _phase_a_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_research_evidence_accumulation" / "daily" / as_of_date


def _phase_a_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_research_evidence_accumulation" / "daily" / as_of_date


def _phase_b_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_readiness_reevaluation_prep" / "daily" / as_of_date


def _phase_b_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_readiness_reevaluation_prep" / "daily" / as_of_date


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
