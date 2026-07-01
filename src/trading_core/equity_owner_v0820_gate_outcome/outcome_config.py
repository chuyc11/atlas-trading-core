"""Configuration for v0.8.20 owner gate outcome."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.20-a-share-owner-readiness-controlled-gate-reevaluation-or-final-blocked-closeout"
BASELINE_VERSION = "v0.8.19-a-share-owner-readiness-evidence-backed-gate-reevaluation-prep"
RECOMMENDED_NEXT_VERSION = "v0.8.21-a-share-owner-readiness-closeout-review-and-v0.9.0-rc-prep"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_v0820_inputs"
DECIDE_BRANCH = "decide_reevaluation_or_closeout_branch"
EXECUTE_CONTROLLED = "execute_controlled_gate_reevaluation"
GENERATE_CLOSEOUT = "generate_final_blocked_closeout"
BUILD_REPORT = "build_v0820_owner_outcome_report"
AUDIT_EXISTING = "audit_existing_v0820_outcome"
BUILD_AND_AUDIT = "build_and_audit_v0820_outcome"
ALLOWED_MODES = [
    VALIDATE_INPUTS,
    DECIDE_BRANCH,
    EXECUTE_CONTROLLED,
    GENERATE_CLOSEOUT,
    BUILD_REPORT,
    AUDIT_EXISTING,
    BUILD_AND_AUDIT,
]

BRANCH_CONTROLLED = "controlled_gate_reevaluation"
BRANCH_CLOSEOUT = "final_blocked_closeout"

FILES = {
    "v0820_outcome_config": "v0820_outcome_config.json",
    "v0820_input_availability": "v0820_input_availability.json",
    "v0820_source_resolution": "v0820_source_resolution.json",
    "v0820_date_alignment": "v0820_date_alignment.json",
    "v0820_branch_decision": "v0820_branch_decision.json",
    "controlled_gate_reevaluation_outcome": "controlled_gate_reevaluation_outcome.json",
    "final_blocked_closeout": "final_blocked_closeout.json",
    "threshold_preservation_check": "threshold_preservation_check.json",
    "waiver_exclusion_check": "waiver_exclusion_check.json",
    "boundary_preservation_check": "boundary_preservation_check.json",
    "v0820_owner_outcome_summary": "v0820_owner_outcome_summary.json",
    "v0820_source_trace": "v0820_source_trace.json",
    "v0820_boundary_check": "v0820_boundary_check.json",
    "v0820_manifest": "v0820_manifest.json",
}

REPORTS = {
    "v0820_owner_gate_outcome_report": "A_SHARE_V0820_OWNER_GATE_OUTCOME.md",
    "v0820_branch_decision_report": "A_SHARE_V0820_BRANCH_DECISION.md",
    "controlled_gate_reevaluation_outcome_report": "A_SHARE_CONTROLLED_GATE_REEVALUATION_OUTCOME.md",
    "final_blocked_closeout_report": "A_SHARE_FINAL_BLOCKED_CLOSEOUT.md",
    "v0820_source_trace_report": "A_SHARE_V0820_SOURCE_TRACE.md",
}

BOUNDARY = {
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
    "execute_remediation_actions": False,
    "external_notifications_sent": False,
    "rerun_build_from_existing_data": False,
    "rerun_daily_pack": False,
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "waiver_used_for_outcome": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "v0820_outcome_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class V0820OutcomeConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_AND_AUDIT
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str, minimum_owner_readiness_score: int) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-V0820-GATE-OUTCOME-CONFIG",
            "target_version": TARGET_VERSION,
            "baseline_version": BASELINE_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "minimum_owner_readiness_score": minimum_owner_readiness_score,
            "v0820_branching_only": True,
            "allow_controlled_reevaluation_if_eligible": True,
            "allow_final_blocked_closeout_if_not_eligible": True,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
            "allow_broker": False,
            "allow_real_orders": False,
            "allow_order_preview": False,
            "allow_buy_sell_signals": False,
            "allow_public_network_refresh": False,
            "allow_full_research_run": False,
            "allow_old_run_daily": False,
            "execute_official_forward_dry_run_day2": False,
            "execute_remediation_actions": False,
            "send_external_notifications": False,
            "does_not_lower_threshold": True,
            "does_not_auto_waive": True,
            "research_only": True,
            "virtual_only": True,
            "not_investment_advice": True,
            "not_order_instruction": True,
            "not_profit_guarantee": True,
            "not_live_trading_ready": True,
            "allow_date_mismatch": self.allow_date_mismatch,
            "raw_config": asdict(self),
        }


def validate_config(config: V0820OutcomeConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_v0820_gate_outcome" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_v0820_gate_outcome" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["v0820_outcome_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_v0820_gate_outcome_audit.json"
    artifacts["v0820_outcome_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_V0820_GATE_OUTCOME_AUDIT.md"
    return artifacts

