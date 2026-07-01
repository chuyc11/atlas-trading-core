"""Configuration for v0.8.18 owner recovery evidence collection."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts"
BASELINE_VERSION = "v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation"
RECOMMENDED_NEXT_VERSION = "v0.8.19-a-share-owner-readiness-evidence-backed-gate-reevaluation-prep"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_recovery_evidence_inputs"
COLLECT_EVIDENCE = "collect_recovery_evidence"
GRADE_QUALITY = "grade_recovery_evidence_quality"
BUILD_IMPROVEMENT = "build_readiness_improvement_artifacts"
BUILD_REPORT = "build_recovery_evidence_report"
AUDIT_EXISTING = "audit_existing_recovery_evidence"
ALLOWED_MODES = [VALIDATE_INPUTS, COLLECT_EVIDENCE, GRADE_QUALITY, BUILD_IMPROVEMENT, BUILD_REPORT, AUDIT_EXISTING]

QUALITY_GRADES = ["none", "weak", "partial", "strong", "audit_verified"]

FILES = {
    "recovery_evidence_config": "recovery_evidence_config.json",
    "recovery_evidence_input_availability": "recovery_evidence_input_availability.json",
    "recovery_evidence_source_resolution": "recovery_evidence_source_resolution.json",
    "recovery_evidence_date_alignment": "recovery_evidence_date_alignment.json",
    "recovery_task_evidence_collection": "recovery_task_evidence_collection.json",
    "developer_follow_up_evidence_package": "developer_follow_up_evidence_package.json",
    "owner_follow_up_evidence_package": "owner_follow_up_evidence_package.json",
    "quality_issue_evidence_package": "quality_issue_evidence_package.json",
    "warning_mapping_evidence_package": "warning_mapping_evidence_package.json",
    "source_trace_improvement_evidence": "source_trace_improvement_evidence.json",
    "markdown_quality_improvement_evidence": "markdown_quality_improvement_evidence.json",
    "artifact_completeness_evidence": "artifact_completeness_evidence.json",
    "readiness_improvement_evidence_ledger": "readiness_improvement_evidence_ledger.json",
    "evidence_backed_score_impact_estimate": "evidence_backed_score_impact_estimate.json",
    "evidence_quality_grading": "evidence_quality_grading.json",
    "evidence_gap_register": "evidence_gap_register.json",
    "remaining_blocker_register": "remaining_blocker_register.json",
    "next_reevaluation_prep_checklist": "next_reevaluation_prep_checklist.json",
    "recovery_evidence_source_trace": "recovery_evidence_source_trace.json",
    "recovery_evidence_boundary_check": "recovery_evidence_boundary_check.json",
    "recovery_evidence_manifest": "recovery_evidence_manifest.json",
    "recovery_evidence_summary": "recovery_evidence_summary.json",
}

REPORTS = {
    "recovery_evidence_collection_report": "A_SHARE_RECOVERY_EVIDENCE_COLLECTION.md",
    "readiness_improvement_evidence_report": "A_SHARE_READINESS_IMPROVEMENT_EVIDENCE.md",
    "recovery_evidence_gaps_report": "A_SHARE_RECOVERY_EVIDENCE_GAPS.md",
    "next_reevaluation_prep_report": "A_SHARE_NEXT_REEVALUATION_PREP.md",
    "recovery_evidence_source_trace_report": "A_SHARE_RECOVERY_EVIDENCE_SOURCE_TRACE.md",
}

BOUNDARY = {
    "recovery_evidence_only": True,
    "readiness_improvement_artifacts_only": True,
    "source_gate_decision_preserved": True,
    "rerun_owner_readiness_gate": False,
    "rerun_build_from_existing_data": False,
    "rerun_daily_pack": False,
    "new_gate_score_generated": False,
    "new_gate_decision_generated": False,
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "public_network_refresh_run": False,
    "full_research_run": False,
    "old_run_daily_called": False,
    "run_daily_called": False,
    "day2_executed": False,
    "external_notifications_sent": False,
    "execute_remediation_actions": False,
    "research_only": True,
    "virtual_only": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "recovery_evidence_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]
FORBIDDEN_EVIDENCE_TYPES = {"broker_connected", "order_submitted", "trade_executed", "buy_signal_generated", "sell_signal_generated", "real_account_checked"}


@dataclass(frozen=True)
class RecoveryEvidenceConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = COLLECT_EVIDENCE
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str, source_readiness_score: int, minimum_owner_readiness_score: int) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-RECOVERY-EVIDENCE-CONFIG",
            "target_version": TARGET_VERSION,
            "baseline_version": BASELINE_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "source_readiness_score": source_readiness_score,
            "minimum_owner_readiness_score": minimum_owner_readiness_score,
            "recovery_evidence_only": True,
            "readiness_improvement_artifacts_only": True,
            "rerun_owner_readiness_gate": False,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
            "generate_new_gate_score": False,
            "generate_new_gate_decision": False,
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


def validate_config(config: RecoveryEvidenceConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_recovery_evidence" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_recovery_evidence" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["recovery_evidence_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_recovery_evidence_audit.json"
    artifacts["recovery_evidence_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_RECOVERY_EVIDENCE_AUDIT.md"
    return artifacts

