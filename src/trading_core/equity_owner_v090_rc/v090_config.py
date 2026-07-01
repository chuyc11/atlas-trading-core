"""Configuration for v0.9.0 owner-readiness RC closeout."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression"
BASELINE_VERSION = "v0.8.21-a-share-owner-readiness-closeout-review-and-v0.9.0-rc-prep"
RECOMMENDED_NEXT_VERSION = "v0.9.1-a-share-owner-daily-run-operator-experience-and-known-blocked-state-hardening"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_v090_rc_inputs"
RUN_FULL_REGRESSION = "run_v090_full_regression"
RUN_AUDIT_SWEEP = "run_v090_audit_sweep"
RUN_BOUNDARY_TRACE_SWEEP = "run_v090_boundary_and_trace_sweep"
VERIFY_DOCS_FREEZE = "verify_v090_documentation_freeze"
BUILD_RC_REPORT = "build_v090_rc_report"
AUDIT_EXISTING = "audit_existing_v090_rc"
ALLOWED_MODES = [
    VALIDATE_INPUTS,
    RUN_FULL_REGRESSION,
    RUN_AUDIT_SWEEP,
    RUN_BOUNDARY_TRACE_SWEEP,
    VERIFY_DOCS_FREEZE,
    BUILD_RC_REPORT,
    AUDIT_EXISTING,
]

FILES = {
    "v090_rc_config": "v090_rc_config.json",
    "v090_input_availability": "v090_input_availability.json",
    "v090_source_resolution": "v090_source_resolution.json",
    "v090_date_alignment": "v090_date_alignment.json",
    "v090_full_pytest_result": "v090_full_pytest_result.json",
    "v090_audit_sweep_result": "v090_audit_sweep_result.json",
    "v090_boundary_sweep_result": "v090_boundary_sweep_result.json",
    "v090_source_trace_sweep_result": "v090_source_trace_sweep_result.json",
    "v090_documentation_freeze_result": "v090_documentation_freeze_result.json",
    "v090_known_blocked_state_disclosure": "v090_known_blocked_state_disclosure.json",
    "v090_release_candidate_decision": "v090_release_candidate_decision.json",
    "v090_owner_release_summary": "v090_owner_release_summary.json",
    "v090_source_trace": "v090_source_trace.json",
    "v090_boundary_check": "v090_boundary_check.json",
    "v090_manifest": "v090_manifest.json",
}

REPORTS = {
    "v090_rc_report": "A_SHARE_V090_RC_REPORT.md",
    "v090_full_regression_report": "A_SHARE_V090_FULL_REGRESSION_RESULT.md",
    "v090_audit_sweep_report": "A_SHARE_V090_AUDIT_SWEEP_RESULT.md",
    "v090_known_blocked_state_report": "A_SHARE_V090_KNOWN_BLOCKED_STATE_DISCLOSURE.md",
    "v090_release_candidate_decision_report": "A_SHARE_V090_RELEASE_CANDIDATE_DECISION.md",
    "v090_source_trace_report": "A_SHARE_V090_SOURCE_TRACE.md",
}

BOUNDARY = {
    "v090_rc_with_known_blocked_owner_readiness_state": True,
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
    "threshold_lowered": False,
    "auto_waiver_allowed": False,
    "manual_waiver_approval_recorded": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "v090_rc_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]


@dataclass(frozen=True)
class V090RCConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = RUN_FULL_REGRESSION
    allow_date_mismatch: bool = False
    skip_full_pytest: bool = False

    def to_dict(self, *, source: dict[str, Any]) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-V090-RC-CONFIG",
            "target_version": TARGET_VERSION,
            "baseline_version": BASELINE_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_gate_decision": source.get("source_gate_decision"),
            "known_owner_readiness_state": "blocked",
            "previous_readiness_score": source.get("previous_readiness_score"),
            "minimum_owner_readiness_score": source.get("minimum_owner_readiness_score"),
            "score_gap": source.get("score_gap"),
            "owner_operationally_acceptable": source.get("owner_operationally_acceptable"),
            "blocked_state_intentional": source.get("blocked_state_intentional"),
            "blocked_state_audited": source.get("blocked_state_audited"),
            "blocked_state_misrepresented_as_acceptable": source.get("blocked_state_misrepresented_as_acceptable"),
            "v090_rc_with_known_blocked_owner_readiness_state": True,
            "run_full_pytest": not self.skip_full_pytest,
            "run_full_audit_sweep": True,
            "run_boundary_sweep": True,
            "run_source_trace_sweep": True,
            "verify_documentation_freeze": True,
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
            "skip_full_pytest": self.skip_full_pytest,
            "releasable": not self.skip_full_pytest,
            "raw_config": asdict(self),
        }


def validate_config(config: V090RCConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_v090_rc" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_v090_rc" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["v090_rc_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_v090_rc_audit.json"
    artifacts["v090_rc_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_V090_RC_AUDIT.md"
    return artifacts
