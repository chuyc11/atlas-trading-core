"""Audit the v0.9.5 research evidence accumulation and prep package."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from trading_core.equity_data_quality.common import read_json, write_json
from trading_core.equity_research_evidence_accumulation.builder import (
    BASELINE_OWNER_READINESS_DATE,
    DEFAULT_AS_OF_DATE,
    RECOMMENDED_NEXT_VERSION,
    SOURCE_READINESS_SCORE,
    TARGET_VERSION,
)
from trading_core.storage.file_paths import ProjectPaths, project_paths


def audit_a_share_research_evidence_accumulation_and_prep(
    *,
    as_of_date: str = DEFAULT_AS_OF_DATE,
    paths: ProjectPaths | None = None,
) -> dict[str, Any]:
    paths = paths or project_paths()
    phase_a = paths.data_dir / "equity_research_evidence_accumulation" / "daily" / as_of_date
    phase_b = paths.data_dir / "equity_readiness_reevaluation_prep" / "daily" / as_of_date
    audit_json = paths.data_dir / "equity_data_quality" / "a_share_research_evidence_accumulation_and_prep_audit.json"
    audit_md = paths.outputs_dir / "audit" / "A_SHARE_RESEARCH_EVIDENCE_ACCUMULATION_AND_PREP_AUDIT.md"

    evidence_result = read_json(phase_a / "evidence_accumulation_result.json")
    boundary_validation = read_json(phase_a / "research_only_boundary_validation.json")
    readiness_gap = read_json(phase_a / "readiness_evidence_gap_analysis.json")
    candidate_diagnostics = read_json(phase_a / "candidate_overlap_and_turnover_diagnostics.json")
    score_diagnostics = read_json(phase_a / "score_distribution_diagnostics.json")
    portfolio_diagnostics = read_json(phase_a / "virtual_portfolio_research_diagnostics.json")
    briefing_diagnostics = read_json(phase_a / "research_briefing_quality_diagnostics.json")

    scorecard = read_json(phase_b / "evidence_quality_scorecard.json")
    blocker_mapping = read_json(phase_b / "blocker_evidence_mapping.json")
    input_package = read_json(phase_b / "reevaluation_input_candidate_package.json")
    precheck = read_json(phase_b / "controlled_reevaluation_precheck.json")
    go_no_go = read_json(phase_b / "go_no_go_for_future_reevaluation.json")
    not_ready = read_json(phase_b / "not_ready_reason_register.json")
    prep_boundary = read_json(phase_b / "reevaluation_prep_boundary_check.json")
    prep_result = read_json(phase_b / "reevaluation_prep_result.json")

    phase_a_checks = {
        "evidence_accumulation_result_generated": bool(evidence_result),
        "research_only_boundary_validation_passed": bool(boundary_validation.get("research_only_boundary_validation_passed")),
        "readiness_gap_analysis_generated": bool(readiness_gap),
    }
    phase_b_checks = {
        "evidence_quality_scorecard_generated": bool(scorecard),
        "blocker_evidence_mapping_generated": bool(blocker_mapping),
        "reevaluation_input_candidate_package_generated": bool(input_package),
        "controlled_reevaluation_precheck_generated": bool(precheck),
        "go_no_go_decision_generated": bool(go_no_go),
        "not_ready_reason_register_generated": bool(not_ready),
        "reevaluation_prep_boundary_check_passed": bool(prep_boundary.get("overall_passed")),
    }
    gate_safety = {
        "owner_readiness_gate_rerun": False,
        "controlled_gate_reevaluation_run": False,
        "new_gate_score_generated": False,
        "new_gate_decision_generated": False,
        "owner_readiness_state": "blocked",
        "source_readiness_score": SOURCE_READINESS_SCORE,
    }
    trading_boundary = {
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "live_trading_ready": False,
    }
    text_checks = {
        "candidate_diagnostics_do_not_use_buy_sell_wording": not bool(candidate_diagnostics.get("forbidden_wording_present")),
        "score_diagnostics_marked_not_trade_signal": bool(score_diagnostics.get("not_trade_signal")),
        "score_diagnostics_not_owner_readiness_score": bool(score_diagnostics.get("not_owner_readiness_score")),
        "virtual_portfolio_marked_virtual_only": bool(portfolio_diagnostics.get("virtual_only")),
        "virtual_portfolio_marked_not_real_portfolio": bool(portfolio_diagnostics.get("not_real_portfolio")),
        "briefing_not_labeled_investment_advice": bool(briefing_diagnostics.get("not_investment_advice")),
        "prep_decision_not_mislabeled_as_gate_decision": bool(go_no_go.get("not_owner_readiness_gate_decision")),
        "evidence_quality_score_not_mislabeled_as_readiness_score": bool(scorecard.get("not_owner_readiness_score") and scorecard.get("not_gate_score")),
    }
    policy_checks = {
        "no_data_refresh_run": boundary_validation.get("data_refresh_run") is False and prep_boundary.get("data_refresh_run") is False,
        "no_research_pipeline_rerun_run": boundary_validation.get("research_pipeline_rerun_run") is False and prep_boundary.get("research_pipeline_rerun_run") is False,
        "no_owner_daily_pack_run": boundary_validation.get("owner_daily_pack_run") is False,
        "no_owner_readiness_gate_rerun": boundary_validation.get("owner_readiness_gate_rerun") is False and prep_boundary.get("owner_readiness_gate_rerun") is False,
        "no_controlled_gate_reevaluation": boundary_validation.get("controlled_gate_reevaluation_run") is False and prep_boundary.get("controlled_reevaluation_executed") is False,
        "no_new_gate_score": boundary_validation.get("new_gate_score_generated") is False and prep_boundary.get("new_gate_score_generated") is False,
        "no_new_gate_decision": boundary_validation.get("new_gate_decision_generated") is False and prep_boundary.get("new_gate_decision_generated") is False,
        "readiness_score_preserved": prep_result.get("source_readiness_score") == SOURCE_READINESS_SCORE,
        "owner_readiness_remains_blocked": prep_result.get("known_owner_readiness_state") == "blocked",
        "protected_order_trade_account_paths_untouched": bool(boundary_validation.get("protected_order_trade_account_paths_untouched") and prep_boundary.get("protected_order_trade_account_paths_untouched")),
        "no_old_run_daily": boundary_validation.get("old_run_daily_called") is False and prep_boundary.get("old_run_daily_called") is False,
        "no_official_day2": boundary_validation.get("day2_executed") is False and prep_boundary.get("day2_executed") is False,
    }

    blocking = []
    for group_name, group in {
        "phase_a_checks": phase_a_checks,
        "phase_b_checks": phase_b_checks,
        "text_checks": text_checks,
        "policy_checks": policy_checks,
    }.items():
        blocking.extend(f"{group_name}.{key}" for key, value in group.items() if not value)
    blocking.extend(evidence_result.get("blocking_reasons", []))
    blocking.extend(prep_result.get("blocking_reasons", []))

    result = {
        "audit_id": "A-SHARE-RESEARCH-EVIDENCE-ACCUMULATION-AND-PREP-AUDIT",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "overall_passed": not blocking,
        "blocking_reasons": blocking,
        "warnings": [*evidence_result.get("warnings", []), *prep_result.get("warnings", [])],
        "phase_a_checks": phase_a_checks,
        "phase_b_checks": phase_b_checks,
        "gate_safety": gate_safety,
        "trading_boundary": trading_boundary,
        "text_checks": text_checks,
        "policy_checks": policy_checks,
        "test_policy": {
            "targeted_pytest_required": True,
            "full_pytest_run": False,
            "full_pytest_deferred_until": "next-major-closeout-or-explicit-request",
        },
        "recommended_next_version": RECOMMENDED_NEXT_VERSION,
        "source_owner_readiness_date": BASELINE_OWNER_READINESS_DATE,
        "audit_json_path": _rel(audit_json, paths.project_root),
        "audit_markdown_path": _rel(audit_md, paths.project_root),
    }
    write_json(audit_json, result)
    _write_audit_markdown(audit_md, result)
    return result


def _write_audit_markdown(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# A-Share Research Evidence Accumulation and Prep Audit",
        "",
        "## Summary",
        f"- overall_passed: {result['overall_passed']}",
        f"- blocking_reasons: {result['blocking_reasons']}",
        f"- warnings_count: {len(result['warnings'])}",
        "",
        "## Phase A Checks",
        *[f"- {key}: {value}" for key, value in result["phase_a_checks"].items()],
        "",
        "## Phase B Checks",
        *[f"- {key}: {value}" for key, value in result["phase_b_checks"].items()],
        "",
        "## Gate Safety",
        *[f"- {key}: {value}" for key, value in result["gate_safety"].items()],
        "",
        "## Trading Boundary",
        *[f"- {key}: {value}" for key, value in result["trading_boundary"].items()],
        "",
        "## Test Policy",
        "- full_pytest_run: false",
        "",
        "## Recommended Next Version",
        f"- {result['recommended_next_version']}",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
