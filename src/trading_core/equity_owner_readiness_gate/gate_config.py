"""Configuration for v0.8.13 owner readiness gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.8.13-a-share-owner-readiness-gate-and-daily-pack-quality-thresholds"
BASELINE_VERSION = "v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends"
RECOMMENDED_NEXT_VERSION = "v0.8.14-a-share-owner-daily-pack-quality-exceptions-and-escalation-workflow"
DEFAULT_AS_OF_DATE = "2026-06-26"
SOURCE_WORKFLOW_MODE = "build_from_existing_data"
DEFAULT_MINIMUM_OWNER_READINESS_SCORE = 75

VALIDATE_INPUTS = "validate_owner_readiness_gate_inputs"
BUILD_POLICY = "build_owner_readiness_threshold_policy"
EVALUATE_GATE = "evaluate_owner_readiness_gate"
BUILD_REPORT = "build_owner_readiness_gate_report"
AUDIT_EXISTING = "audit_existing_owner_readiness_gate"
ALLOWED_MODES = [VALIDATE_INPUTS, BUILD_POLICY, EVALUATE_GATE, BUILD_REPORT, AUDIT_EXISTING]

FILES = {
    "owner_readiness_gate_config": "owner_readiness_gate_config.json",
    "owner_readiness_gate_input_availability": "owner_readiness_gate_input_availability.json",
    "owner_readiness_gate_source_resolution": "owner_readiness_gate_source_resolution.json",
    "owner_readiness_gate_date_alignment": "owner_readiness_gate_date_alignment.json",
    "owner_readiness_threshold_policy": "owner_readiness_threshold_policy.json",
    "daily_pack_quality_threshold_policy": "daily_pack_quality_threshold_policy.json",
    "owner_readiness_score_gate": "owner_readiness_score_gate.json",
    "daily_pack_completeness_gate": "daily_pack_completeness_gate.json",
    "warning_issue_quality_gate": "warning_issue_quality_gate.json",
    "safe_action_quality_gate": "safe_action_quality_gate.json",
    "protected_path_quality_gate": "protected_path_quality_gate.json",
    "boundary_quality_gate": "boundary_quality_gate.json",
    "source_trace_quality_gate": "source_trace_quality_gate.json",
    "trend_sufficiency_quality_gate": "trend_sufficiency_quality_gate.json",
    "markdown_report_quality_gate": "markdown_report_quality_gate.json",
    "artifact_navigation_quality_gate": "artifact_navigation_quality_gate.json",
    "owner_next_step_quality_gate": "owner_next_step_quality_gate.json",
    "owner_readiness_gate_decision": "owner_readiness_gate_decision.json",
    "quality_threshold_evaluation": "quality_threshold_evaluation.json",
    "quality_exception_candidate_list": "quality_exception_candidate_list.json",
    "owner_release_recommendation": "owner_release_recommendation.json",
    "owner_readiness_gate_source_trace": "owner_readiness_gate_source_trace.json",
    "owner_readiness_gate_boundary_check": "owner_readiness_gate_boundary_check.json",
    "owner_readiness_gate_manifest": "owner_readiness_gate_manifest.json",
    "owner_readiness_gate_summary": "owner_readiness_gate_summary.json",
}

REPORTS = {
    "owner_readiness_gate_report": "A_SHARE_OWNER_READINESS_GATE.md",
    "daily_pack_quality_thresholds_report": "A_SHARE_DAILY_PACK_QUALITY_THRESHOLDS.md",
    "owner_release_recommendation_report": "A_SHARE_OWNER_RELEASE_RECOMMENDATION.md",
    "quality_exception_candidates_report": "A_SHARE_QUALITY_EXCEPTION_CANDIDATES.md",
    "owner_readiness_gate_source_trace_report": "A_SHARE_OWNER_READINESS_GATE_SOURCE_TRACE.md",
}

BOUNDARY = {
    "owner_readiness_gate_only": True,
    "quality_thresholds_only": True,
    "not_investment_gate": True,
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
    "owner_readiness_gate_used_as_trade_instruction": False,
    "protected_path_modifications_detected": False,
}

FORBIDDEN_RECOMMENDATIONS = {"buy_stock", "sell_stock", "place_order", "rebalance_real_account", "connect_broker", "enable_live_trading"}
FORBIDDEN_ARTIFACT_NAMES = {"BROKER_ORDER.json", "REAL_ORDER.json", "ORDER_PREVIEW.md", "BUY_LIST.md", "SELL_LIST.md"}
FORBIDDEN_POSITIVE_WORDING = ["买入建议", "卖出建议", "下单建议", "保证盈利", "实盘就绪", "推荐买入", "买入信号", "卖出信号"]
FORBIDDEN_SAFE_ACTION_MARKERS = ["broker", "order", "trade", "buy", "sell", "下单", "买入", "卖出", "实盘"]


@dataclass(frozen=True)
class OwnerReadinessGateConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = EVALUATE_GATE
    minimum_owner_readiness_score: int = DEFAULT_MINIMUM_OWNER_READINESS_SCORE
    allow_date_mismatch: bool = False
    allow_known_non_blocking_warnings: bool = True
    allow_insufficient_history_if_correctly_flagged: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-OWNER-READINESS-GATE-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "source_workflow_mode": SOURCE_WORKFLOW_MODE,
            "minimum_owner_readiness_score": self.minimum_owner_readiness_score,
            "owner_facing": True,
            "machine_readable": True,
            "generate_markdown": True,
            "owner_operations_gate_only": True,
            "not_investment_gate": True,
            "rerun_build_from_existing_data": False,
            "rerun_daily_pack": False,
            "rerun_daily_pack_history": False,
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
            "allow_known_non_blocking_warnings": self.allow_known_non_blocking_warnings,
            "allow_insufficient_history_if_correctly_flagged": self.allow_insufficient_history_if_correctly_flagged,
            "raw_config": asdict(self),
        }


def validate_config(config: OwnerReadinessGateConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {ALLOWED_MODES}")
    if not 0 <= config.minimum_owner_readiness_score <= 100:
        issues.append("minimum_owner_readiness_score must be between 0 and 100")
    return issues


def data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_owner_readiness_gate" / "daily" / as_of_date


def output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_owner_readiness_gate" / "daily" / as_of_date


def artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    ddir = data_dir(paths, as_of_date)
    odir = output_dir(paths, as_of_date)
    artifacts = {key: ddir / name for key, name in FILES.items()}
    artifacts.update({key: odir / name for key, name in REPORTS.items()})
    artifacts["owner_readiness_gate_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json"
    artifacts["owner_readiness_gate_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_OWNER_READINESS_GATE_AUDIT.md"
    return artifacts
