"""Configuration for v0.8.15 owner readiness recovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.15-a-share-owner-readiness-recovery-plan-and-quality-improvement-loop"
BASELINE_VERSION = "v0.8.14-a-share-owner-daily-pack-quality-exceptions-and-escalation-workflow"
RECOMMENDED_NEXT_VERSION = "v0.8.16-a-share-owner-readiness-recovery-execution-tracker-and-gate-reevaluation-prep"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_recovery_inputs"
ANALYZE_GAP = "analyze_readiness_gap"
BUILD_IMPROVEMENT = "build_quality_improvement_plan"
BUILD_VERIFICATION = "build_recovery_verification_plan"
BUILD_REPORT = "build_owner_recovery_report"
AUDIT_EXISTING = "audit_existing_recovery_plan"
ALLOWED_MODES = [VALIDATE_INPUTS, ANALYZE_GAP, BUILD_IMPROVEMENT, BUILD_VERIFICATION, BUILD_REPORT, AUDIT_EXISTING]

FILES = {
    "recovery_plan_config": "recovery_plan_config.json",
    "recovery_input_availability": "recovery_input_availability.json",
    "recovery_source_resolution": "recovery_source_resolution.json",
    "recovery_date_alignment": "recovery_date_alignment.json",
    "readiness_gap_summary": "readiness_gap_summary.json",
    "score_driver_analysis": "score_driver_analysis.json",
    "quality_exception_root_cause_map": "quality_exception_root_cause_map.json",
    "quality_improvement_target_policy": "quality_improvement_target_policy.json",
    "recovery_task_backlog": "recovery_task_backlog.json",
    "developer_follow_up_recovery_plan": "developer_follow_up_recovery_plan.json",
    "owner_follow_up_recovery_plan": "owner_follow_up_recovery_plan.json",
    "non_actionable_recovery_items": "non_actionable_recovery_items.json",
    "recovery_score_impact_model": "recovery_score_impact_model.json",
    "recovery_milestone_plan": "recovery_milestone_plan.json",
    "quality_improvement_loop_definition": "quality_improvement_loop_definition.json",
    "recovery_verification_plan": "recovery_verification_plan.json",
    "gate_reevaluation_readiness_checklist": "gate_reevaluation_readiness_checklist.json",
    "blocked_state_preservation_check": "blocked_state_preservation_check.json",
    "recovery_risk_register": "recovery_risk_register.json",
    "recovery_source_trace": "recovery_source_trace.json",
    "recovery_boundary_check": "recovery_boundary_check.json",
    "recovery_manifest": "recovery_manifest.json",
    "recovery_summary": "recovery_summary.json",
}

REPORTS = {
    "owner_readiness_recovery_plan_report": "A_SHARE_OWNER_READINESS_RECOVERY_PLAN.md",
    "readiness_gap_summary_report": "A_SHARE_READINESS_GAP_SUMMARY.md",
    "quality_improvement_task_backlog_report": "A_SHARE_QUALITY_IMPROVEMENT_TASK_BACKLOG.md",
    "developer_recovery_follow_up_report": "A_SHARE_DEVELOPER_RECOVERY_FOLLOW_UP.md",
    "gate_reevaluation_readiness_checklist_report": "A_SHARE_GATE_REEVALUATION_READINESS_CHECKLIST.md",
    "recovery_source_trace_report": "A_SHARE_RECOVERY_SOURCE_TRACE.md",
}

BOUNDARY = {
    "recovery_plan_only": True,
    "quality_improvement_loop_only": True,
    "blocked_gate_decision_preserved": True,
    "recovery_plan_changes_gate_decision": False,
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "execute_recovery_tasks": False,
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
    "external_notifications_sent": False,
    "public_network_refresh_run": False,
    "full_research_run": False,
    "execute_remediation_actions": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "recovery_plan_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

ALLOWED_TASK_CATEGORIES = {
    "improve_pack_completeness",
    "improve_source_trace_quality",
    "improve_markdown_quality",
    "document_known_warning",
    "resolve_warning_source",
    "clarify_owner_next_step",
    "wait_for_more_history",
    "developer_follow_up",
    "audit_only_verification",
    "boundary_policy_check",
    "protected_path_policy_check",
}
FORBIDDEN_TASK_CATEGORIES = {"buy_stock", "sell_stock", "place_order", "cancel_order", "rebalance_account", "connect_broker", "read_real_account", "enable_live_trading"}
FORBIDDEN_COMMAND_FRAGMENTS = ["run-daily", "broker", "order", "trade", "easytrader", "THSTrader", "buy", "sell"]
FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class RecoveryPlanConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_IMPROVEMENT
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str, minimum_score: int, actual_score: int, score_gap: int) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-READINESS-RECOVERY-PLAN-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "preserve_blocked_gate_decision": True,
            "minimum_owner_readiness_score": minimum_score,
            "actual_owner_readiness_score": actual_score,
            "readiness_score_gap": score_gap,
            "recovery_plan_only": True,
            "quality_improvement_loop_only": True,
            "does_not_change_gate_decision": True,
            "does_not_lower_threshold": True,
            "does_not_auto_waive": True,
            "execute_recovery_tasks": False,
            "mark_tasks_complete_by_default": False,
            "rerun_build_from_existing_data": False,
            "rerun_owner_readiness_gate": False,
            "rerun_daily_pack": False,
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


def validate_config(config: RecoveryPlanConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_readiness_recovery" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_readiness_recovery" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["recovery_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_recovery_audit.json"
    artifacts["recovery_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_READINESS_RECOVERY_AUDIT.md"
    return artifacts
