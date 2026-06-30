"""Configuration for v0.8.11 owner daily pack."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack"
BASELINE_VERSION = "v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh"
RECOMMENDED_NEXT_VERSION = "v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_INPUTS = "validate_daily_pack_inputs"
RESOLVE_SOURCES = "resolve_daily_pack_sources"
BUILD_RUNBOOK = "build_owner_daily_runbook"
BUILD_DECISION_PACK = "build_owner_operations_decision_pack"
AUDIT_EXISTING = "audit_existing_daily_pack"
ALLOWED_MODES = [VALIDATE_INPUTS, RESOLVE_SOURCES, BUILD_RUNBOOK, BUILD_DECISION_PACK, AUDIT_EXISTING]

SOURCE_WORKFLOW_MODE = "build_from_existing_data"

BOUNDARY = {
    "daily_pack_only": True,
    "owner_operations_decision_pack_only": True,
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
    "official_forward_dry_run_status_unchanged": True,
    "external_notifications_sent": False,
    "public_network_refresh_run": False,
    "full_research_run": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
    "real_account_data_read": False,
    "daily_pack_used_as_trade_instruction": False,
}

FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

ALLOWED_OPERATIONAL_DECISION_CATEGORIES = {
    "no_action_required",
    "review_warnings",
    "review_safe_actions",
    "inspect_artifacts",
    "wait_for_more_history",
    "developer_follow_up",
    "rerun_audit_only",
    "hold_release",
}

FORBIDDEN_DECISION_CATEGORIES = {
    "buy_stock",
    "sell_stock",
    "place_order",
    "rebalance_real_account",
    "connect_broker",
    "enable_live_trading",
}

FORBIDDEN_SAFE_ACTION_TYPES = {"place_order", "connect_broker", "read_real_account", "generate_order_preview"}

FORBIDDEN_ARTIFACT_NAMES = {
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
}

FORBIDDEN_POSITIVE_WORDING = [
    "买入建议",
    "卖出建议",
    "下单建议",
    "保证盈利",
    "实盘就绪",
    "推荐买入",
    "买入信号",
    "卖出信号",
]

FILES = {
    "daily_pack_config": "daily_pack_config.json",
    "daily_pack_input_availability": "daily_pack_input_availability.json",
    "daily_pack_source_resolution": "daily_pack_source_resolution.json",
    "daily_pack_date_alignment": "daily_pack_date_alignment.json",
    "owner_daily_status_brief": "owner_daily_status_brief.json",
    "owner_daily_runbook": "owner_daily_runbook.json",
    "owner_operations_decision_pack": "owner_operations_decision_pack.json",
    "owner_next_step_checklist": "owner_next_step_checklist.json",
    "research_output_digest": "research_output_digest.json",
    "candidate_tracking_digest": "candidate_tracking_digest.json",
    "virtual_portfolio_digest": "virtual_portfolio_digest.json",
    "warning_issue_digest": "warning_issue_digest.json",
    "safe_action_digest": "safe_action_digest.json",
    "monitoring_remediation_ops_digest": "monitoring_remediation_ops_digest.json",
    "protected_path_digest": "protected_path_digest.json",
    "source_trace_digest": "source_trace_digest.json",
    "boundary_digest": "boundary_digest.json",
    "daily_pack_artifact_navigation": "daily_pack_artifact_navigation.json",
    "daily_pack_source_trace": "daily_pack_source_trace.json",
    "daily_pack_boundary_check": "daily_pack_boundary_check.json",
    "daily_pack_manifest": "daily_pack_manifest.json",
    "daily_pack_summary": "daily_pack_summary.json",
}

REPORTS = {
    "owner_daily_decision_pack_report": "A_SHARE_OWNER_DAILY_DECISION_PACK.md",
    "owner_daily_runbook_report": "A_SHARE_OWNER_DAILY_RUNBOOK.md",
    "owner_daily_status_brief_report": "A_SHARE_OWNER_DAILY_STATUS_BRIEF.md",
    "owner_next_step_checklist_report": "A_SHARE_OWNER_NEXT_STEP_CHECKLIST.md",
    "research_output_digest_report": "A_SHARE_RESEARCH_OUTPUT_DIGEST.md",
    "owner_daily_pack_source_trace_report": "A_SHARE_OWNER_DAILY_PACK_SOURCE_TRACE.md",
}


@dataclass(frozen=True)
class DailyPackConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = BUILD_DECISION_PACK
    allow_date_mismatch: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-DAILY-PACK-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "owner_facing": True,
            "machine_readable": True,
            "generate_markdown": True,
            "decision_pack_type": "owner_operations_decision_pack",
            "not_investment_decision_pack": True,
            "prefer_build_output_ops_refresh": True,
            "rerun_build_from_existing_data": False,
            "rerun_ops_refresh": False,
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
            **FLAGS,
            "raw_config": asdict(self),
        }


def validate_config(config: DailyPackConfig) -> list[str]:
    issues = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_daily_pack" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_daily_pack" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["owner_daily_pack_audit_json"] = (
        paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_audit.json"
    )
    artifacts["owner_daily_pack_audit_report"] = (
        paths.outputs_dir / "audit" / "A_SHARE_OWNER_DAILY_PACK_AUDIT.md"
    )
    return artifacts

