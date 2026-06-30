"""Configuration for v0.8.16 owner readiness recovery execution tracking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.16-a-share-owner-readiness-recovery-execution-tracker-and-gate-reevaluation-prep"
BASELINE_VERSION = "v0.8.15-a-share-owner-readiness-recovery-plan-and-quality-improvement-loop"
RECOMMENDED_NEXT_VERSION = "v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_recovery_execution_inputs"
COLLECT_EVIDENCE = "collect_recovery_evidence"
EVALUATE_STATUS = "evaluate_recovery_task_status"
PREPARE_REEVALUATION = "prepare_gate_reevaluation"
BUILD_REPORT = "build_recovery_execution_report"
AUDIT_EXISTING = "audit_existing_recovery_execution"
ALLOWED_MODES = [VALIDATE_INPUTS, COLLECT_EVIDENCE, EVALUATE_STATUS, PREPARE_REEVALUATION, BUILD_REPORT, AUDIT_EXISTING]

FILES = {
    "recovery_execution_config": "recovery_execution_config.json",
    "recovery_execution_input_availability": "recovery_execution_input_availability.json",
    "recovery_execution_source_resolution": "recovery_execution_source_resolution.json",
    "recovery_execution_date_alignment": "recovery_execution_date_alignment.json",
    "recovery_task_evidence_registry": "recovery_task_evidence_registry.json",
    "recovery_task_status_tracker": "recovery_task_status_tracker.json",
    "developer_follow_up_evidence_tracker": "developer_follow_up_evidence_tracker.json",
    "owner_follow_up_evidence_tracker": "owner_follow_up_evidence_tracker.json",
    "audit_only_verification_evidence": "audit_only_verification_evidence.json",
    "recovery_task_completion_evaluation": "recovery_task_completion_evaluation.json",
    "recovery_evidence_quality_assessment": "recovery_evidence_quality_assessment.json",
    "score_impact_evidence_assessment": "score_impact_evidence_assessment.json",
    "readiness_improvement_evidence_summary": "readiness_improvement_evidence_summary.json",
    "gate_reevaluation_prerequisite_checklist": "gate_reevaluation_prerequisite_checklist.json",
    "gate_reevaluation_readiness_decision": "gate_reevaluation_readiness_decision.json",
    "controlled_reevaluation_plan": "controlled_reevaluation_plan.json",
    "blocked_state_preservation_check": "blocked_state_preservation_check.json",
    "threshold_preservation_check": "threshold_preservation_check.json",
    "waiver_preservation_check": "waiver_preservation_check.json",
    "recovery_execution_source_trace": "recovery_execution_source_trace.json",
    "recovery_execution_boundary_check": "recovery_execution_boundary_check.json",
    "recovery_execution_manifest": "recovery_execution_manifest.json",
    "recovery_execution_summary": "recovery_execution_summary.json",
}

REPORTS = {
    "recovery_execution_tracker_report": "A_SHARE_RECOVERY_EXECUTION_TRACKER.md",
    "recovery_task_evidence_report": "A_SHARE_RECOVERY_TASK_EVIDENCE.md",
    "gate_reevaluation_prep_report": "A_SHARE_GATE_REEVALUATION_PREP.md",
    "controlled_reevaluation_plan_report": "A_SHARE_CONTROLLED_REEVALUATION_PLAN.md",
    "recovery_execution_source_trace_report": "A_SHARE_RECOVERY_EXECUTION_SOURCE_TRACE.md",
}

BOUNDARY = {
    "recovery_execution_tracker_only": True,
    "gate_reevaluation_prep_only": True,
    "blocked_gate_decision_preserved": True,
    "recovery_execution_changes_gate_decision": False,
    "gate_reevaluation_executed": False,
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
    "recovery_execution_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

ALLOWED_EVIDENCE_TYPES = {
    "artifact_exists",
    "audit_passed",
    "source_trace_complete",
    "boundary_clean",
    "warning_mapped",
    "developer_note",
    "owner_review_note",
    "history_observation_added",
    "documentation_updated",
}
FORBIDDEN_EVIDENCE_TYPES = {"broker_connected", "order_submitted", "trade_executed", "buy_signal_generated", "sell_signal_generated", "real_account_checked"}
ALLOWED_TASK_STATUSES = {"planned", "in_progress", "evidence_available", "verified_by_audit_only", "blocked", "not_actionable", "waiting_for_more_history"}
FORBIDDEN_COMMAND_FRAGMENTS = ["run-daily", "broker", "order", "trade", "easytrader", "thstrader", "buy", "sell"]
FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class RecoveryExecutionConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = PREPARE_REEVALUATION
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str, minimum_score: int, actual_score: int) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-READINESS-RECOVERY-EXECUTION-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "preserve_blocked_gate_decision": True,
            "minimum_owner_readiness_score": minimum_score,
            "actual_owner_readiness_score": actual_score,
            "recovery_execution_tracker_only": True,
            "gate_reevaluation_prep_only": True,
            "execute_recovery_tasks": False,
            "rerun_owner_readiness_gate": False,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
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


def validate_config(config: RecoveryExecutionConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_readiness_recovery_execution" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["recovery_execution_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_recovery_execution_audit.json"
    artifacts["recovery_execution_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_READINESS_RECOVERY_EXECUTION_AUDIT.md"
    return artifacts
