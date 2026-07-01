"""Configuration for v0.9.1 owner/operator experience hardening."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths

TARGET_VERSION = "v0.9.1-a-share-owner-daily-run-operator-experience-and-known-blocked-state-hardening"
SOURCE_RELEASE_CANDIDATE = "v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression"
RECOMMENDED_NEXT_VERSION = "v0.9.2-a-share-owner-daily-status-artifact-navigation-and-report-usability"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"

VALIDATE_INPUTS = "validate_operator_experience_inputs"
BUILD_STATUS = "build_owner_daily_status"
BUILD_BLOCKED_HARDENING = "build_known_blocked_state_hardening"
BUILD_NAV_ACTIONS = "build_operator_navigation_and_actions"
BUILD_REPORT = "build_operator_experience_report"
AUDIT_EXISTING = "audit_existing_operator_experience"
ALLOWED_MODES = [
    VALIDATE_INPUTS,
    BUILD_STATUS,
    BUILD_BLOCKED_HARDENING,
    BUILD_NAV_ACTIONS,
    BUILD_REPORT,
    AUDIT_EXISTING,
]

FILES = {
    "operator_experience_config": "operator_experience_config.json",
    "operator_input_availability": "operator_input_availability.json",
    "operator_source_resolution": "operator_source_resolution.json",
    "operator_date_alignment": "operator_date_alignment.json",
    "owner_daily_status_card": "owner_daily_status_card.json",
    "known_blocked_state_banner": "known_blocked_state_banner.json",
    "known_blocked_state_explanation": "known_blocked_state_explanation.json",
    "operator_capability_matrix": "operator_capability_matrix.json",
    "operator_action_menu": "operator_action_menu.json",
    "artifact_navigation_index": "artifact_navigation_index.json",
    "owner_next_step_decision_aid": "owner_next_step_decision_aid.json",
    "rc_status_summary": "rc_status_summary.json",
    "audit_and_test_status_summary": "audit_and_test_status_summary.json",
    "safety_boundary_status_panel": "safety_boundary_status_panel.json",
    "unresolved_blocker_digest": "unresolved_blocker_digest.json",
    "operator_source_trace": "operator_source_trace.json",
    "operator_boundary_check": "operator_boundary_check.json",
    "operator_manifest": "operator_manifest.json",
    "operator_summary": "operator_summary.json",
}

REPORTS = {
    "owner_daily_status_report": "A_SHARE_OWNER_DAILY_OPERATOR_STATUS.md",
    "known_blocked_state_guide": "A_SHARE_KNOWN_BLOCKED_STATE_GUIDE.md",
    "operator_action_menu_report": "A_SHARE_OPERATOR_ACTION_MENU.md",
    "artifact_navigation_report": "A_SHARE_ARTIFACT_NAVIGATION_INDEX.md",
    "operator_quickstart": "A_SHARE_OPERATOR_QUICKSTART.md",
    "operator_source_trace_report": "A_SHARE_OPERATOR_SOURCE_TRACE.md",
}

BOUNDARY = {
    "operator_experience_only": True,
    "known_blocked_state_hardening_only": True,
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
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "operator_experience_used_as_trade_instruction": False,
}

FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]
FORBIDDEN_ACTION_TYPES = {
    "place_order",
    "connect_broker",
    "read_real_account",
    "generate_order_preview",
    "generate_buy_signal",
    "generate_sell_signal",
    "rerun_owner_readiness_gate",
    "rerun_build_from_existing_data",
    "rerun_daily_pack",
    "call_old_run_daily",
    "execute_day2",
}


@dataclass(frozen=True)
class OperatorExperienceConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_STATUS
    allow_date_mismatch: bool = False

    def to_dict(self, *, source: dict[str, Any]) -> dict[str, Any]:
        score = source.get("previous_readiness_score")
        threshold = source.get("minimum_owner_readiness_score")
        return {
            "config_id": "A-SHARE-OWNER-OPERATOR-EXPERIENCE-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "source_release_candidate": SOURCE_RELEASE_CANDIDATE,
            "known_owner_readiness_state": "blocked",
            "owner_operationally_acceptable": source.get("owner_operationally_acceptable"),
            "previous_readiness_score": score,
            "minimum_owner_readiness_score": threshold,
            "score_gap": source.get("score_gap", (threshold - score) if isinstance(score, int) and isinstance(threshold, int) else None),
            "operator_experience_only": True,
            "known_blocked_state_hardening_only": True,
            "rerun_owner_readiness_gate": False,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
            "generate_new_gate_score": False,
            "generate_new_gate_decision": False,
            "run_full_pytest": False,
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


def validate_config(config: OperatorExperienceConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_operator_experience" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_operator_experience" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["operator_experience_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_operator_experience_audit.json"
    artifacts["operator_experience_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_OPERATOR_EXPERIENCE_AUDIT.md"
    return artifacts
