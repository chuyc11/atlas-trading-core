"""Configuration for v0.8.14 owner quality exception workflow."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.14-a-share-owner-daily-pack-quality-exceptions-and-escalation-workflow"
BASELINE_VERSION = "v0.8.13-a-share-owner-readiness-gate-and-daily-pack-quality-thresholds"
RECOMMENDED_NEXT_VERSION = "v0.8.15-a-share-owner-readiness-recovery-plan-and-quality-improvement-loop"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_quality_exception_inputs"
INTAKE_GATE = "intake_blocked_owner_readiness_gate"
CLASSIFY_EXCEPTIONS = "classify_quality_exceptions"
BUILD_ESCALATION = "build_escalation_workflow"
BUILD_REPORT = "build_owner_exception_report"
AUDIT_EXISTING = "audit_existing_quality_exception_workflow"
ALLOWED_MODES = [VALIDATE_INPUTS, INTAKE_GATE, CLASSIFY_EXCEPTIONS, BUILD_ESCALATION, BUILD_REPORT, AUDIT_EXISTING]

FILES = {
    "quality_exception_workflow_config": "quality_exception_workflow_config.json",
    "quality_exception_input_availability": "quality_exception_input_availability.json",
    "quality_exception_source_resolution": "quality_exception_source_resolution.json",
    "quality_exception_date_alignment": "quality_exception_date_alignment.json",
    "blocked_gate_intake": "blocked_gate_intake.json",
    "quality_exception_registry": "quality_exception_registry.json",
    "quality_exception_classification": "quality_exception_classification.json",
    "owner_readiness_gap_analysis": "owner_readiness_gap_analysis.json",
    "threshold_failure_explanation": "threshold_failure_explanation.json",
    "waiver_candidate_evaluation": "waiver_candidate_evaluation.json",
    "manual_waiver_policy": "manual_waiver_policy.json",
    "manual_waiver_request_template": "manual_waiver_request_template.json",
    "manual_waiver_decision_record": "manual_waiver_decision_record.json",
    "escalation_workflow": "escalation_workflow.json",
    "developer_follow_up_tracker": "developer_follow_up_tracker.json",
    "owner_follow_up_checklist": "owner_follow_up_checklist.json",
    "blocked_daily_pack_owner_notice": "blocked_daily_pack_owner_notice.json",
    "exception_severity_matrix": "exception_severity_matrix.json",
    "exception_routing_matrix": "exception_routing_matrix.json",
    "exception_sla_policy": "exception_sla_policy.json",
    "exception_audit_trail": "exception_audit_trail.json",
    "quality_exception_source_trace": "quality_exception_source_trace.json",
    "quality_exception_boundary_check": "quality_exception_boundary_check.json",
    "quality_exception_manifest": "quality_exception_manifest.json",
    "quality_exception_summary": "quality_exception_summary.json",
}

REPORTS = {
    "quality_exception_workflow_report": "A_SHARE_OWNER_QUALITY_EXCEPTION_WORKFLOW.md",
    "blocked_daily_pack_owner_notice_report": "A_SHARE_BLOCKED_DAILY_PACK_OWNER_NOTICE.md",
    "owner_readiness_gap_analysis_report": "A_SHARE_OWNER_READINESS_GAP_ANALYSIS.md",
    "escalation_workflow_report": "A_SHARE_ESCALATION_WORKFLOW.md",
    "manual_waiver_policy_report": "A_SHARE_MANUAL_WAIVER_POLICY.md",
    "developer_follow_up_tracker_report": "A_SHARE_DEVELOPER_FOLLOW_UP_TRACKER.md",
    "quality_exception_source_trace_report": "A_SHARE_QUALITY_EXCEPTION_SOURCE_TRACE.md",
}

BOUNDARY = {
    "quality_exception_workflow_only": True,
    "preserve_blocked_gate_decision": True,
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
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "waiver_changes_gate_decision": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "quality_exception_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ROUTES = {"place_order", "connect_broker", "enable_live_trading", "rebalance_account", "buy_stock", "sell_stock"}
FORBIDDEN_COMMAND_FRAGMENTS = ["run-daily", "broker", "order", "trade", "easytrader", "THSTrader", "buy", "sell"]
FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class QualityExceptionWorkflowConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_ESCALATION
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str = "blocked") -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-QUALITY-EXCEPTION-WORKFLOW-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "owner_readiness_gate_decision": source_gate_decision,
            "preserve_blocked_gate_decision": True,
            "allow_auto_waiver": False,
            "manual_waiver_supported": True,
            "manual_waiver_approval_recorded": False,
            "waiver_changes_gate_decision": False,
            "exception_workflow_only": True,
            "not_investment_exception": True,
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


def validate_config(config: QualityExceptionWorkflowConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_quality_exceptions" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_quality_exceptions" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["quality_exception_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_quality_exception_workflow_audit.json"
    artifacts["quality_exception_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_QUALITY_EXCEPTION_WORKFLOW_AUDIT.md"
    return artifacts
