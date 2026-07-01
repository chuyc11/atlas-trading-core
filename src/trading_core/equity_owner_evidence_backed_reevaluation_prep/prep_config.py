"""Configuration for v0.8.19 evidence-backed reevaluation prep."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.8.19-a-share-owner-readiness-evidence-backed-gate-reevaluation-prep"
BASELINE_VERSION = "v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts"
RECOMMENDED_NEXT_VERSION = "v0.8.20-a-share-owner-readiness-controlled-gate-reevaluation-or-final-blocked-closeout"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_evidence_backed_prep_inputs"
EVALUATE_SUFFICIENCY = "evaluate_evidence_sufficiency_for_reevaluation"
BUILD_INPUT_PACKAGE = "build_reevaluation_input_package"
BUILD_NEXT_PLAN = "build_next_controlled_reevaluation_plan"
BUILD_REPORT = "build_evidence_backed_prep_report"
AUDIT_EXISTING = "audit_existing_evidence_backed_prep"
ALLOWED_MODES = [
    VALIDATE_INPUTS,
    EVALUATE_SUFFICIENCY,
    BUILD_INPUT_PACKAGE,
    BUILD_NEXT_PLAN,
    BUILD_REPORT,
    AUDIT_EXISTING,
]

FILES = {
    "evidence_backed_prep_config": "evidence_backed_prep_config.json",
    "evidence_backed_prep_input_availability": "evidence_backed_prep_input_availability.json",
    "evidence_backed_prep_source_resolution": "evidence_backed_prep_source_resolution.json",
    "evidence_backed_prep_date_alignment": "evidence_backed_prep_date_alignment.json",
    "evidence_sufficiency_for_reevaluation_decision": "evidence_sufficiency_for_reevaluation_decision.json",
    "evidence_to_gate_mapping": "evidence_to_gate_mapping.json",
    "reevaluation_input_package": "reevaluation_input_package.json",
    "score_impact_readiness_summary": "score_impact_readiness_summary.json",
    "gate_threshold_preservation_package": "gate_threshold_preservation_package.json",
    "waiver_exclusion_package": "waiver_exclusion_package.json",
    "boundary_preservation_package": "boundary_preservation_package.json",
    "evidence_backed_readiness_checklist": "evidence_backed_readiness_checklist.json",
    "remaining_evidence_gap_decision": "remaining_evidence_gap_decision.json",
    "controlled_reevaluation_eligibility_decision": "controlled_reevaluation_eligibility_decision.json",
    "next_gate_reevaluation_execution_plan": "next_gate_reevaluation_execution_plan.json",
    "evidence_backed_prep_source_trace": "evidence_backed_prep_source_trace.json",
    "evidence_backed_prep_boundary_check": "evidence_backed_prep_boundary_check.json",
    "evidence_backed_prep_manifest": "evidence_backed_prep_manifest.json",
    "evidence_backed_prep_summary": "evidence_backed_prep_summary.json",
}

REPORTS = {
    "evidence_backed_gate_reevaluation_prep_report": "A_SHARE_EVIDENCE_BACKED_GATE_REEVALUATION_PREP.md",
    "reevaluation_input_package_report": "A_SHARE_REEVALUATION_INPUT_PACKAGE.md",
    "evidence_sufficiency_decision_report": "A_SHARE_EVIDENCE_SUFFICIENCY_DECISION.md",
    "next_gate_reevaluation_plan_report": "A_SHARE_NEXT_GATE_REEVALUATION_PLAN.md",
    "evidence_backed_prep_source_trace_report": "A_SHARE_EVIDENCE_BACKED_PREP_SOURCE_TRACE.md",
}

BOUNDARY = {
    "evidence_backed_prep_only": True,
    "reevaluation_input_package_only": True,
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
    "rerun_owner_readiness_gate": False,
    "rerun_build_from_existing_data": False,
    "rerun_daily_pack": False,
    "new_gate_score_generated": False,
    "new_gate_decision_generated": False,
    "source_gate_decision_preserved": True,
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "evidence_backed_prep_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class EvidenceBackedPrepConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = EVALUATE_SUFFICIENCY
    allow_date_mismatch: bool = False

    def to_dict(self, *, source_gate_decision: str, source_readiness_score: int, minimum_owner_readiness_score: int) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-EVIDENCE-BACKED-REEVALUATION-PREP-CONFIG",
            "target_version": TARGET_VERSION,
            "baseline_version": BASELINE_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source_gate_decision,
            "source_readiness_score": source_readiness_score,
            "minimum_owner_readiness_score": minimum_owner_readiness_score,
            "evidence_backed_prep_only": True,
            "reevaluation_input_package_only": True,
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


def validate_config(config: EvidenceBackedPrepConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["evidence_backed_prep_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_evidence_backed_reevaluation_prep_audit.json"
    artifacts["evidence_backed_prep_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_EVIDENCE_BACKED_REEVALUATION_PREP_AUDIT.md"
    return artifacts

