"""Configuration for v0.7.9 A-share daily research workflow orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.7.9-a-share-daily-workflow-orchestration"
RECOMMENDED_NEXT_VERSION = "v0.7.10-a-share-benchmark-data-and-performance-comparison"
REMEDIATION_VERSION = "v0.7.9.1-a-share-daily-workflow-orchestration-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

VALIDATE_EXISTING_ARTIFACTS = "validate_existing_artifacts"
BUILD_FROM_EXISTING_DATA = "build_from_existing_data"
FULL_RESEARCH_RUN = "full_research_run"
ALLOWED_MODES = (VALIDATE_EXISTING_ARTIFACTS, BUILD_FROM_EXISTING_DATA, FULL_RESEARCH_RUN)

WORKFLOW_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_real_trade": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

WORKFLOW_BOUNDARY = {
    "workflow_orchestration_only": True,
    "call_old_run_daily": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}

WORKFLOW_FILES = {
    "workflow_config": "workflow_config.json",
    "workflow_preflight": "workflow_preflight.json",
    "workflow_stage_manifest": "workflow_stage_manifest.json",
    "workflow_run_manifest": "workflow_run_manifest.json",
    "workflow_source_trace": "workflow_source_trace.json",
    "workflow_boundary_check": "workflow_boundary_check.json",
    "workflow_summary": "workflow_summary.json",
}

WORKFLOW_REPORTS = {
    "workflow_summary_report": "A_SHARE_DAILY_WORKFLOW_SUMMARY.md",
    "workflow_stage_report": "A_SHARE_DAILY_WORKFLOW_STAGE_REPORT.md",
    "workflow_source_trace_report": "A_SHARE_DAILY_WORKFLOW_SOURCE_TRACE.md",
}

INPUT_VERSIONS = {
    "tradable_universe": "v0.7.2",
    "features": "v0.7.3",
    "scores": "v0.7.4",
    "candidates": "v0.7.5",
    "virtual_portfolios": "v0.7.6",
    "briefing": "v0.7.7",
    "tracking": "v0.7.8",
}

REQUIRED_WORKFLOW_COMMANDS = [
    "preflight-a-share-daily-workflow",
    "run-a-share-daily-research-workflow",
    "audit-a-share-daily-research-workflow",
    "run-and-audit-a-share-daily-research-workflow",
]

FORBIDDEN_OUTPUT_NAMES = {
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "order_preview.json",
    "broker_order.json",
    "real_order.json",
    "buy_list.json",
    "sell_list.json",
}

FORBIDDEN_SOURCE_PATH_TOKENS = {
    "tests/fixtures",
    "sample",
    "mock",
    "external_research",
    "day_002",
    "day_003",
    "broker",
    "orders",
    "trades",
    "accounts",
    "run_daily",
    "run-daily",
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
    "guaranteed profit",
    "live trading ready: true",
    "strong buy",
    "must buy",
]


@dataclass(frozen=True)
class WorkflowConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    mode: str = VALIDATE_EXISTING_ARTIFACTS
    allow_public_data_refresh: bool = False
    allow_latest_artifact_date: bool = False
    allow_build_timestamp_drift: bool = True
    fail_on_build_timestamp_drift: bool = False
    allow_version_shim_warning: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-DAILY-RESEARCH-WORKFLOW-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "mode": self.mode,
            "allowed_modes": list(ALLOWED_MODES),
            "allow_public_data_refresh": self.allow_public_data_refresh,
            "allow_latest_artifact_date": self.allow_latest_artifact_date,
            "allow_build_timestamp_drift": self.allow_build_timestamp_drift,
            "fail_on_build_timestamp_drift": self.fail_on_build_timestamp_drift,
            "call_old_run_daily": False,
            "execute_official_forward_dry_run_day2": False,
            "broker_enabled": False,
            "real_order_enabled": False,
            "build_timestamp_non_strict_idempotency": True,
            **WORKFLOW_FLAGS,
            "boundary": dict(WORKFLOW_BOUNDARY),
            "raw_config": asdict(self),
        }


def validate_workflow_config(config: WorkflowConfig) -> list[str]:
    issues: list[str] = []
    if config.mode not in ALLOWED_MODES:
        issues.append(f"mode must be one of {', '.join(ALLOWED_MODES)}")
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.fail_on_build_timestamp_drift and config.allow_build_timestamp_drift:
        issues.append("fail_on_build_timestamp_drift requires allow_build_timestamp_drift=false")
    if config.mode != FULL_RESEARCH_RUN and config.allow_public_data_refresh:
        issues.append("allow_public_data_refresh is only valid for full_research_run")
    return issues


def workflow_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_workflows" / "daily" / as_of_date


def workflow_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_workflows" / "daily" / as_of_date


def workflow_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = workflow_data_dir(paths, as_of_date)
    output_dir = workflow_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in WORKFLOW_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in WORKFLOW_REPORTS.items()})
    artifacts["workflow_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_daily_workflow_audit.json"
    artifacts["workflow_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_DAILY_WORKFLOW_AUDIT.md"
    return artifacts


def required_input_artifacts(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    return {
        "history_dir": paths.data_dir / "equity_market" / "history",
        "tradable_universe": paths.data_dir / "equity_selection" / "daily" / as_of_date / "tradable_universe.json",
        "tradable_universe_manifest": paths.data_dir / "equity_selection" / "daily" / as_of_date / "tradable_universe_manifest.json",
        "feature_manifest": paths.data_dir / "equity_features" / "daily" / as_of_date / "feature_manifest.json",
        "score_manifest": paths.data_dir / "equity_scores" / "daily" / as_of_date / "score_manifest.json",
        "candidate_manifest": paths.data_dir / "equity_selection" / "daily" / as_of_date / "candidate_manifest.json",
        "portfolio_manifest": paths.data_dir / "equity_portfolios" / "daily" / as_of_date / "portfolio_manifest.json",
        "briefing_manifest": paths.data_dir / "equity_briefings" / "daily" / as_of_date / "briefing_manifest.json",
        "tracking_manifest": paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date / "tracking_manifest.json",
    }


def upstream_audit_artifacts(paths: ProjectPaths) -> dict[str, Path]:
    audit_dir = paths.data_dir / "equity_data_quality"
    return {
        "tradable_universe": audit_dir / "a_share_tradable_universe_audit.json",
        "features": audit_dir / "a_share_multi_horizon_feature_audit.json",
        "scores": audit_dir / "a_share_scoring_audit.json",
        "candidates": audit_dir / "a_share_candidate_generation_audit.json",
        "virtual_portfolios": audit_dir / "a_share_virtual_portfolio_construction_audit.json",
        "briefing": audit_dir / "a_share_daily_stock_selection_briefing_audit.json",
        "tracking": audit_dir / "a_share_virtual_portfolio_tracking_audit.json",
    }


def stage_definitions(paths: ProjectPaths, as_of_date: str) -> list[dict[str, Any]]:
    inputs = required_input_artifacts(paths, as_of_date)
    audits = upstream_audit_artifacts(paths)
    workflow_artifacts = workflow_artifact_paths(paths, as_of_date)
    return [
        {
            "stage_id": "stage_00_preflight",
            "stage_name": "preflight",
            "stage_order": 0,
            "validate_command": f"python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date {as_of_date}",
            "build_command": f"python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date {as_of_date}",
            "input_artifacts": ["VERSION", "src/trading_core/__init__.py", "trading_core/__init__.py"],
            "output_artifacts": [workflow_artifacts["workflow_preflight"]],
            "audit_artifacts": [],
        },
        {
            "stage_id": "stage_01_data_readiness",
            "stage_name": "data_readiness",
            "stage_order": 1,
            "validate_command": "verify required A-share research artifacts",
            "build_command": "verify historical A-share data panels",
            "input_artifacts": list(inputs.values()),
            "output_artifacts": [],
            "audit_artifacts": [],
        },
        _upstream_stage(
            stage_id="stage_02_tradable_universe",
            stage_name="tradable_universe",
            stage_order=2,
            as_of_date=as_of_date,
            command_base="build-and-audit-a-share-tradable-universe",
            validate_artifacts=[inputs["tradable_universe"], inputs["tradable_universe_manifest"]],
            audit_artifact=audits["tradable_universe"],
        ),
        _upstream_stage(
            stage_id="stage_03_feature_engineering",
            stage_name="feature_engineering",
            stage_order=3,
            as_of_date=as_of_date,
            command_base="build-and-audit-a-share-multi-horizon-features",
            validate_artifacts=[inputs["feature_manifest"]],
            audit_artifact=audits["features"],
        ),
        _upstream_stage(
            stage_id="stage_04_scoring",
            stage_name="scoring",
            stage_order=4,
            as_of_date=as_of_date,
            command_base="build-and-audit-a-share-scores",
            validate_artifacts=[inputs["score_manifest"]],
            audit_artifact=audits["scores"],
        ),
        _upstream_stage(
            stage_id="stage_05_candidate_generation",
            stage_name="candidate_generation",
            stage_order=5,
            as_of_date=as_of_date,
            command_base="generate-and-audit-a-share-candidates",
            validate_artifacts=[inputs["candidate_manifest"]],
            audit_artifact=audits["candidates"],
        ),
        _upstream_stage(
            stage_id="stage_06_virtual_portfolio_construction",
            stage_name="virtual_portfolio_construction",
            stage_order=6,
            as_of_date=as_of_date,
            command_base="build-and-audit-a-share-virtual-portfolios",
            validate_artifacts=[inputs["portfolio_manifest"]],
            audit_artifact=audits["virtual_portfolios"],
        ),
        _upstream_stage(
            stage_id="stage_07_daily_briefing",
            stage_name="daily_briefing",
            stage_order=7,
            as_of_date=as_of_date,
            command_base="build-and-audit-a-share-daily-stock-selection-briefing",
            validate_artifacts=[inputs["briefing_manifest"]],
            audit_artifact=audits["briefing"],
        ),
        _upstream_stage(
            stage_id="stage_08_virtual_portfolio_tracking",
            stage_name="virtual_portfolio_tracking",
            stage_order=8,
            as_of_date=as_of_date,
            command_base="build-and-audit-a-share-virtual-portfolio-tracking",
            validate_artifacts=[inputs["tracking_manifest"]],
            audit_artifact=audits["tracking"],
        ),
        {
            "stage_id": "stage_09_workflow_audit",
            "stage_name": "workflow_audit",
            "stage_order": 9,
            "validate_command": f"python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date {as_of_date}",
            "build_command": f"python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date {as_of_date}",
            "input_artifacts": [
                workflow_artifacts["workflow_config"],
                workflow_artifacts["workflow_preflight"],
                workflow_artifacts["workflow_stage_manifest"],
                workflow_artifacts["workflow_run_manifest"],
                workflow_artifacts["workflow_source_trace"],
                workflow_artifacts["workflow_boundary_check"],
            ],
            "output_artifacts": [workflow_artifacts["workflow_audit_json"], workflow_artifacts["workflow_audit_report"]],
            "audit_artifacts": [workflow_artifacts["workflow_audit_json"]],
        },
        {
            "stage_id": "stage_10_owner_summary",
            "stage_name": "owner_summary",
            "stage_order": 10,
            "validate_command": "write owner-facing A-share daily workflow summary",
            "build_command": "write owner-facing A-share daily workflow summary",
            "input_artifacts": [workflow_artifacts["workflow_run_manifest"], workflow_artifacts["workflow_boundary_check"]],
            "output_artifacts": [workflow_artifacts["workflow_summary_report"], workflow_artifacts["workflow_stage_report"]],
            "audit_artifacts": [],
        },
    ]


def _upstream_stage(
    *,
    stage_id: str,
    stage_name: str,
    stage_order: int,
    as_of_date: str,
    command_base: str,
    validate_artifacts: list[Path],
    audit_artifact: Path,
) -> dict[str, Any]:
    return {
        "stage_id": stage_id,
        "stage_name": stage_name,
        "stage_order": stage_order,
        "validate_command": f"verify existing artifacts for {stage_name}",
        "build_command": f"python -m trading_core.cli {command_base} --as-of-date {as_of_date}",
        "input_artifacts": validate_artifacts,
        "output_artifacts": validate_artifacts,
        "audit_artifacts": [audit_artifact],
    }
