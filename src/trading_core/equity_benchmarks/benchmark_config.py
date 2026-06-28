"""Configuration for v0.7.10 A-share benchmark comparison."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from trading_core.storage.file_paths import ProjectPaths


TARGET_VERSION = "v0.7.10-a-share-benchmark-data-and-performance-comparison"
RECOMMENDED_NEXT_VERSION = "v0.7.11-a-share-multi-day-portfolio-performance-tracking"
REMEDIATION_VERSION = "v0.7.10.1-a-share-benchmark-comparison-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"
DEFAULT_LOOKBACK_TRADING_DAYS = 250
DEFAULT_MINIMUM_REQUIRED_TRADING_DAYS = 20

BENCHMARK_IDS = [
    "CSI300",
    "CSI500",
    "CSI1000",
    "CASH",
    "EQUAL_WEIGHT_STRICT_TRADABLE",
    "EQUAL_WEIGHT_CANDIDATE_POOL",
]

INDEX_BENCHMARK_IDS = ["CSI300", "CSI500", "CSI1000"]
PORTFOLIO_KEYS = ["long", "mid", "short"]
PORTFOLIO_IDS = {
    "long": "long_virtual_portfolio",
    "mid": "mid_virtual_portfolio",
    "short": "short_virtual_portfolio",
}
INDEX_CODE_MAP = {
    "CSI300": ["000300.SH", "399300.SZ"],
    "CSI500": ["000905.SH"],
    "CSI1000": ["000852.SH"],
}
EASTMONEY_SECID_MAP = {
    "CSI300": "1.000300",
    "CSI500": "1.000905",
    "CSI1000": "1.000852",
}

BENCHMARK_FLAGS = {
    "research_only": True,
    "virtual_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

BENCHMARK_BOUNDARY = {
    "benchmark_comparison_only": True,
    "research_only": True,
    "virtual_only": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "run_daily_called": False,
    "day2_executed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}

BENCHMARK_FILES = {
    "benchmark_config": "benchmark_config.json",
    "benchmark_data_availability": "benchmark_data_availability.json",
    "benchmark_universe_snapshot": "benchmark_universe_snapshot.json",
    "benchmark_price_snapshot": "benchmark_price_snapshot.json",
    "benchmark_return_snapshot": "benchmark_return_snapshot.json",
    "benchmark_nav_snapshot": "benchmark_nav_snapshot.json",
    "portfolio_benchmark_comparison": "portfolio_benchmark_comparison.json",
    "relative_performance_snapshot": "relative_performance_snapshot.json",
    "benchmark_exclusion_report": "benchmark_exclusion_report.json",
    "benchmark_source_trace": "benchmark_source_trace.json",
    "benchmark_manifest": "benchmark_manifest.json",
    "benchmark_boundary_check": "benchmark_boundary_check.json",
    "benchmark_summary": "benchmark_summary.json",
}

BENCHMARK_REPORTS = {
    "benchmark_summary_report": "A_SHARE_BENCHMARK_SUMMARY.md",
    "portfolio_benchmark_comparison_report": "PORTFOLIO_BENCHMARK_COMPARISON.md",
    "benchmark_data_availability_report": "BENCHMARK_DATA_AVAILABILITY.md",
    "benchmark_source_trace_report": "BENCHMARK_SOURCE_TRACE.md",
}

FORBIDDEN_ARTIFACTS = [
    "BROKER_ORDER.json",
    "REAL_ORDER.json",
    "ORDER_PREVIEW.md",
    "BUY_LIST.md",
    "SELL_LIST.md",
    "data/orders",
    "data/trades",
    "data/accounts",
    "outputs/orders",
    "outputs/trades",
    "outputs/accounts",
]

FORBIDDEN_SOURCE_PATH_TOKENS = [
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
]

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
class BenchmarkConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    lookback_trading_days: int = DEFAULT_LOOKBACK_TRADING_DAYS
    minimum_required_trading_days: int = DEFAULT_MINIMUM_REQUIRED_TRADING_DAYS
    allow_placeholder_benchmarks: bool = False
    fail_on_placeholder_benchmarks: bool = True
    currency: str = "CNY"
    cash_benchmark_daily_return: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-BENCHMARK-COMPARISON-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "currency": self.currency,
            "benchmark_ids": list(BENCHMARK_IDS),
            "index_code_map": {key: list(value) for key, value in INDEX_CODE_MAP.items()},
            "price_policy": "adjusted_close_if_available_else_close",
            "cash_benchmark_daily_return": self.cash_benchmark_daily_return,
            "lookback_trading_days": self.lookback_trading_days,
            "minimum_required_trading_days": self.minimum_required_trading_days,
            "allow_placeholder_benchmarks": self.allow_placeholder_benchmarks,
            "fail_on_placeholder_benchmarks": self.fail_on_placeholder_benchmarks,
            "broker_enabled": False,
            "real_order_enabled": False,
            **BENCHMARK_FLAGS,
            "boundary": dict(BENCHMARK_BOUNDARY),
            "raw_config": asdict(self),
        }


def validate_benchmark_config(config: BenchmarkConfig) -> list[str]:
    issues: list[str] = []
    if not config.as_of_date or len(config.as_of_date) != 10:
        issues.append("as_of_date must use YYYY-MM-DD")
    if config.lookback_trading_days < config.minimum_required_trading_days:
        issues.append("lookback_trading_days must be >= minimum_required_trading_days")
    if config.minimum_required_trading_days <= 0:
        issues.append("minimum_required_trading_days must be positive")
    if config.allow_placeholder_benchmarks and config.fail_on_placeholder_benchmarks:
        issues.append("allow_placeholder_benchmarks requires fail_on_placeholder_benchmarks=false")
    if config.cash_benchmark_daily_return != 0.0:
        issues.append("cash_benchmark_daily_return must remain 0.0 for v0.7.10")
    return issues


def benchmark_data_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.data_dir / "equity_benchmarks" / "daily" / as_of_date


def benchmark_output_dir(paths: ProjectPaths, as_of_date: str) -> Path:
    return paths.outputs_dir / "equity_benchmarks" / "daily" / as_of_date


def benchmark_history_dir(paths: ProjectPaths) -> Path:
    return paths.data_dir / "equity_benchmarks" / "history"


def benchmark_artifact_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    data_dir = benchmark_data_dir(paths, as_of_date)
    output_dir = benchmark_output_dir(paths, as_of_date)
    artifacts = {key: data_dir / filename for key, filename in BENCHMARK_FILES.items()}
    artifacts.update({key: output_dir / filename for key, filename in BENCHMARK_REPORTS.items()})
    artifacts["benchmark_audit_json"] = paths.data_dir / "equity_data_quality" / "a_share_benchmark_comparison_audit.json"
    artifacts["benchmark_audit_report"] = paths.outputs_dir / "audit" / "A_SHARE_BENCHMARK_COMPARISON_AUDIT.md"
    return artifacts


def index_history_cache_paths(paths: ProjectPaths) -> dict[str, Path]:
    history_dir = benchmark_history_dir(paths)
    return {
        "index_price_history_panel": history_dir / "index_price_history_panel.parquet",
        "index_price_history_manifest": history_dir / "index_price_history_manifest.json",
    }


def candidate_index_panel_paths(paths: ProjectPaths) -> list[Path]:
    return [
        paths.data_dir / "equity_market" / "history" / "index_price_history_panel.parquet",
        paths.data_dir / "equity_market" / "history" / "index_daily_price_history_panel.parquet",
        benchmark_history_dir(paths) / "index_price_history_panel.parquet",
    ]


def required_input_paths(paths: ProjectPaths, as_of_date: str) -> dict[str, Path]:
    selection_dir = paths.data_dir / "equity_selection" / "daily" / as_of_date
    portfolio_dir = paths.data_dir / "equity_portfolios" / "daily" / as_of_date
    tracking_dir = paths.data_dir / "equity_portfolio_tracking" / "daily" / as_of_date
    workflow_dir = paths.data_dir / "equity_workflows" / "daily" / as_of_date
    history_dir = paths.data_dir / "equity_market" / "history"
    return {
        "workflow_config": workflow_dir / "workflow_config.json",
        "workflow_run_manifest": workflow_dir / "workflow_run_manifest.json",
        "workflow_stage_manifest": workflow_dir / "workflow_stage_manifest.json",
        "workflow_source_trace": workflow_dir / "workflow_source_trace.json",
        "workflow_boundary_check": workflow_dir / "workflow_boundary_check.json",
        "workflow_audit": paths.data_dir / "equity_data_quality" / "a_share_daily_workflow_audit.json",
        "tracking_config": tracking_dir / "tracking_config.json",
        "long_paper_ledger": tracking_dir / "long_paper_ledger.json",
        "mid_paper_ledger": tracking_dir / "mid_paper_ledger.json",
        "short_paper_ledger": tracking_dir / "short_paper_ledger.json",
        "long_holdings_snapshot": tracking_dir / "long_holdings_snapshot.json",
        "mid_holdings_snapshot": tracking_dir / "mid_holdings_snapshot.json",
        "short_holdings_snapshot": tracking_dir / "short_holdings_snapshot.json",
        "portfolio_nav_snapshot": tracking_dir / "portfolio_nav_snapshot.json",
        "portfolio_performance_snapshot": tracking_dir / "portfolio_performance_snapshot.json",
        "tracking_manifest": tracking_dir / "tracking_manifest.json",
        "tracking_source_trace": tracking_dir / "tracking_source_trace.json",
        "tracking_summary": tracking_dir / "tracking_summary.json",
        "tradable_universe": selection_dir / "tradable_universe.json",
        "long_candidates": selection_dir / "long_candidates.json",
        "mid_candidates": selection_dir / "mid_candidates.json",
        "short_candidates": selection_dir / "short_candidates.json",
        "multi_horizon_candidates": selection_dir / "multi_horizon_candidates.json",
        "candidate_manifest": selection_dir / "candidate_manifest.json",
        "long_virtual_portfolio": portfolio_dir / "long_virtual_portfolio.json",
        "mid_virtual_portfolio": portfolio_dir / "mid_virtual_portfolio.json",
        "short_virtual_portfolio": portfolio_dir / "short_virtual_portfolio.json",
        "portfolio_manifest": portfolio_dir / "portfolio_manifest.json",
        "daily_price_history": history_dir / "daily_price_history_panel.parquet",
        "adjusted_price_history": history_dir / "adjusted_price_history_panel.parquet",
    }
