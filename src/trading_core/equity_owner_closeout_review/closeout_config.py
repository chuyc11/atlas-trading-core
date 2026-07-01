"""Configuration for v0.8.21 owner-readiness closeout review."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.21-a-share-owner-readiness-closeout-review-and-v0.9.0-rc-prep"
BASELINE_VERSION = "v0.8.20-a-share-owner-readiness-controlled-gate-reevaluation-or-final-blocked-closeout"
RECOMMENDED_NEXT_VERSION = "v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_closeout_review_inputs"
REVIEW_LINEAGE = "review_owner_readiness_closeout_lineage"
BUILD_RC_SCOPE = "build_v090_rc_scope"
BUILD_FULL_REGRESSION_PLAN = "build_v090_full_regression_plan"
BUILD_REPORT = "build_closeout_review_report"
AUDIT_EXISTING = "audit_existing_closeout_review"
ALLOWED_MODES = [
    VALIDATE_INPUTS,
    REVIEW_LINEAGE,
    BUILD_RC_SCOPE,
    BUILD_FULL_REGRESSION_PLAN,
    BUILD_REPORT,
    AUDIT_EXISTING,
]

FILES = {
    "closeout_review_config": "closeout_review_config.json",
    "closeout_input_availability": "closeout_input_availability.json",
    "closeout_source_resolution": "closeout_source_resolution.json",
    "closeout_date_alignment": "closeout_date_alignment.json",
    "v0813_to_v0820_lineage_review": "v0813_to_v0820_lineage_review.json",
    "blocked_decision_lineage": "blocked_decision_lineage.json",
    "readiness_score_lineage": "readiness_score_lineage.json",
    "evidence_insufficiency_lineage": "evidence_insufficiency_lineage.json",
    "final_blocked_closeout_review": "final_blocked_closeout_review.json",
    "unresolved_blocker_register": "unresolved_blocker_register.json",
    "v090_rc_scope_proposal": "v090_rc_scope_proposal.json",
    "v090_full_regression_plan": "v090_full_regression_plan.json",
    "v090_audit_sweep_plan": "v090_audit_sweep_plan.json",
    "v090_documentation_freeze_checklist": "v090_documentation_freeze_checklist.json",
    "v090_release_risk_register": "v090_release_risk_register.json",
    "v090_release_candidate_readiness_decision": "v090_release_candidate_readiness_decision.json",
    "closeout_source_trace": "closeout_source_trace.json",
    "closeout_boundary_check": "closeout_boundary_check.json",
    "closeout_manifest": "closeout_manifest.json",
    "closeout_summary": "closeout_summary.json",
}

REPORTS = {
    "closeout_review_report": "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md",
    "lineage_review_report": "A_SHARE_V0813_TO_V0820_LINEAGE_REVIEW.md",
    "v090_rc_scope_report": "A_SHARE_V090_RC_SCOPE_PROPOSAL.md",
    "v090_full_regression_report": "A_SHARE_V090_FULL_REGRESSION_PLAN.md",
    "v090_release_risk_report": "A_SHARE_V090_RELEASE_RISK_REGISTER.md",
    "closeout_source_trace_report": "A_SHARE_CLOSEOUT_SOURCE_TRACE.md",
}

BOUNDARY = {
    "closeout_review_only": True,
    "v090_rc_prep_only": True,
    "research_only": True,
    "virtual_only": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "run_daily_called": False,
    "old_run_daily_called": False,
    "day2_executed": False,
    "public_network_refresh_run": False,
    "full_research_run": False,
    "external_notifications_sent": False,
    "execute_remediation_actions": False,
    "rerun_owner_readiness_gate": False,
    "rerun_build_from_existing_data": False,
    "rerun_daily_pack": False,
    "new_gate_score_generated": False,
    "new_gate_decision_generated": False,
    "execute_full_pytest": False,
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "closeout_review_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class CloseoutReviewConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_RC_SCOPE
    allow_date_mismatch: bool = False

    def to_dict(
        self,
        *,
        source_gate_decision: str,
        selected_v0820_branch: str,
        previous_readiness_score: int | None,
        minimum_owner_readiness_score: int | None,
        score_gap: int | None,
    ) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-CLOSEOUT-REVIEW-CONFIG",
            "target_version": TARGET_VERSION,
            "baseline_version": BASELINE_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "selected_v0820_branch": selected_v0820_branch,
            "previous_readiness_score": previous_readiness_score,
            "minimum_owner_readiness_score": minimum_owner_readiness_score,
            "score_gap": score_gap,
            "closeout_review_only": True,
            "v090_rc_prep_only": True,
            "rerun_owner_readiness_gate": False,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
            "generate_new_gate_score": False,
            "generate_new_gate_decision": False,
            "execute_full_pytest": False,
            "does_not_change_gate_decision": True,
            "does_not_lower_threshold": True,
            "does_not_auto_waive": True,
            "execute_remediation_actions": False,
            "send_external_notifications": False,
            "allow_public_network_refresh": False,
            "allow_full_research_run": False,
            "allow_broker": False,
            "allow_real_orders": False,
            "allow_order_preview": False,
            "allow_buy_sell_signals": False,
            "allow_old_run_daily": False,
            "execute_official_forward_dry_run_day2": False,
            "research_only": True,
            "virtual_only": True,
            "not_investment_advice": True,
            "not_order_instruction": True,
            "not_profit_guarantee": True,
            "not_live_trading_ready": True,
            "allow_date_mismatch": self.allow_date_mismatch,
            "raw_config": asdict(self),
        }


def validate_config(config: CloseoutReviewConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_closeout_review" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_closeout_review" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["closeout_review_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_closeout_review_audit.json"
    artifacts["closeout_review_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_CLOSEOUT_REVIEW_AUDIT.md"
    return artifacts
