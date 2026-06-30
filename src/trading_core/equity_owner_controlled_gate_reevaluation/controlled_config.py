"""Configuration for v0.8.17 owner readiness controlled gate reevaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation"
BASELINE_VERSION = "v0.8.16-a-share-owner-readiness-recovery-execution-tracker-and-gate-reevaluation-prep"
SOURCE_GATE_VERSION = "v0.8.13-a-share-owner-readiness-gate-and-daily-pack-history"
RECOMMENDED_NEXT_VERSION = "v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "controlled_gate_reevaluation_from_existing_recovery_execution"

VALIDATE_INPUTS = "validate_controlled_reevaluation_inputs"
EVALUATE_GUARD = "evaluate_reevaluation_readiness_guard"
BUILD_PLAN = "build_controlled_reevaluation_plan"
RECORD_SKIP = "record_reevaluation_skip_decision"
BUILD_REPORT = "build_controlled_reevaluation_report"
AUDIT_EXISTING = "audit_existing_controlled_reevaluation"
ALLOWED_MODES = [VALIDATE_INPUTS, EVALUATE_GUARD, BUILD_PLAN, RECORD_SKIP, BUILD_REPORT, AUDIT_EXISTING]

FILES = {
    "controlled_reevaluation_config": "controlled_reevaluation_config.json",
    "controlled_reevaluation_input_availability": "controlled_reevaluation_input_availability.json",
    "controlled_reevaluation_source_resolution": "controlled_reevaluation_source_resolution.json",
    "controlled_reevaluation_date_alignment": "controlled_reevaluation_date_alignment.json",
    "reevaluation_readiness_guard": "reevaluation_readiness_guard.json",
    "reevaluation_prerequisite_validation": "reevaluation_prerequisite_validation.json",
    "reevaluation_execution_plan": "reevaluation_execution_plan.json",
    "reevaluation_skip_decision": "reevaluation_skip_decision.json",
    "not_ready_reason_summary": "not_ready_reason_summary.json",
    "source_gate_preservation_check": "source_gate_preservation_check.json",
    "threshold_preservation_check": "threshold_preservation_check.json",
    "waiver_preservation_check": "waiver_preservation_check.json",
    "evidence_sufficiency_check": "evidence_sufficiency_check.json",
    "controlled_reevaluation_decision": "controlled_reevaluation_decision.json",
    "controlled_reevaluation_source_trace": "controlled_reevaluation_source_trace.json",
    "controlled_reevaluation_boundary_check": "controlled_reevaluation_boundary_check.json",
    "controlled_reevaluation_manifest": "controlled_reevaluation_manifest.json",
    "controlled_reevaluation_summary": "controlled_reevaluation_summary.json",
}

REPORTS = {
    "controlled_reevaluation_report": "A_SHARE_CONTROLLED_GATE_REEVALUATION.md",
    "reevaluation_skipped_report": "A_SHARE_REEVALUATION_SKIPPED_NOT_READY.md",
    "readiness_guard_report": "A_SHARE_REEVALUATION_READINESS_GUARD.md",
    "controlled_source_trace_report": "A_SHARE_CONTROLLED_REEVALUATION_SOURCE_TRACE.md",
}

BOUNDARY = {
    "controlled_reevaluation_framework_only": True,
    "reevaluation_skipped_not_ready": True,
    "source_blocked_gate_decision_preserved": True,
    "research_only": True,
    "virtual_only": True,
    "gate_reevaluation_executed": False,
    "rerun_owner_readiness_gate": False,
    "rerun_build_from_existing_data": False,
    "rerun_daily_pack": False,
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "owner_operationally_acceptable": False,
    "new_gate_score_generated": False,
    "new_gate_decision_generated": False,
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
    "real_account_data_read": False,
    "controlled_reevaluation_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class ControlledReevaluationConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = RECORD_SKIP
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str, minimum_score: int, actual_score: int) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-CONTROLLED-GATE-REEVALUATION-CONFIG",
            "target_version": TARGET_VERSION,
            "baseline_version": BASELINE_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "preserve_blocked_gate_decision": True,
            "minimum_owner_readiness_score": minimum_score,
            "actual_owner_readiness_score": actual_score,
            "controlled_reevaluation_framework_only": True,
            "record_skip_decision_when_not_ready": True,
            "rerun_owner_readiness_gate": False,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
            "does_not_change_gate_decision": True,
            "does_not_lower_threshold": True,
            "does_not_auto_waive": True,
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


def validate_config(config: ControlledReevaluationConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["controlled_reevaluation_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_controlled_gate_reevaluation_audit.json"
    artifacts["controlled_reevaluation_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_CONTROLLED_GATE_REEVALUATION_AUDIT.md"
    return artifacts

