"""Configuration for v0.7.8 A-share virtual portfolio tracking."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


TARGET_VERSION = "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger"
RECOMMENDED_NEXT_VERSION = "v0.7.9-a-share-daily-workflow-orchestration"
REMEDIATION_VERSION = "v0.7.8.1-a-share-virtual-portfolio-tracking-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

TRACKING_FLAGS = {
    "virtual_only": True,
    "research_only": True,
    "not_investment_advice": True,
    "not_order_instruction": True,
    "not_real_trade": True,
    "not_profit_guarantee": True,
    "not_live_trading_ready": True,
}

LEDGER_FLAGS = {
    **TRACKING_FLAGS,
    "not_buy_signal": True,
    "not_sell_signal": True,
}

TRACKING_BOUNDARY = {
    "virtual_tracking_only": True,
    "paper_ledger_generated": True,
    "real_portfolio_generated": False,
    "buy_sell_signals_generated": False,
    "order_preview_generated": False,
    "official_forward_dry_run_status_unchanged": True,
    "day2_executed": False,
    "run_daily_called": False,
    "broker_connected": False,
    "real_orders_placed": False,
    "model_profit_guaranteed": False,
    "live_trading_ready": False,
}

TRACKING_FILES = {
    "tracking_config": "tracking_config.json",
    "long_paper_ledger": "long_paper_ledger.json",
    "mid_paper_ledger": "mid_paper_ledger.json",
    "short_paper_ledger": "short_paper_ledger.json",
    "long_holdings_snapshot": "long_holdings_snapshot.json",
    "mid_holdings_snapshot": "mid_holdings_snapshot.json",
    "short_holdings_snapshot": "short_holdings_snapshot.json",
    "portfolio_nav_snapshot": "portfolio_nav_snapshot.json",
    "portfolio_performance_snapshot": "portfolio_performance_snapshot.json",
    "portfolio_drawdown_snapshot": "portfolio_drawdown_snapshot.json",
    "portfolio_exposure_snapshot": "portfolio_exposure_snapshot.json",
    "benchmark_comparison_snapshot": "benchmark_comparison_snapshot.json",
    "tracking_manifest": "tracking_manifest.json",
    "tracking_source_trace": "tracking_source_trace.json",
    "tracking_summary": "tracking_summary.json",
}

TRACKING_REPORTS = {
    "tracking_summary_report": "VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md",
    "long_tracking_report": "LONG_PORTFOLIO_TRACKING.md",
    "mid_tracking_report": "MID_PORTFOLIO_TRACKING.md",
    "short_tracking_report": "SHORT_PORTFOLIO_TRACKING.md",
    "benchmark_comparison_report": "BENCHMARK_COMPARISON.md",
}

PORTFOLIO_KEYS = ["long", "mid", "short"]
PORTFOLIO_IDS = {
    "long": "long_virtual_portfolio",
    "mid": "mid_virtual_portfolio",
    "short": "short_virtual_portfolio",
}
PORTFOLIO_HORIZONS = {
    "long": "Long",
    "mid": "Mid",
    "short": "Short",
}

ALLOWED_LEDGER_RECORD_TYPES = {
    "virtual_initial_position",
    "virtual_mark_to_market",
    "virtual_cash_balance",
}

FORBIDDEN_LEDGER_RECORD_TYPES = {
    "buy_order",
    "sell_order",
    "real_trade",
    "broker_fill",
    "order_preview",
}

DEFAULT_BENCHMARKS = ["CSI300", "CSI500", "CSI1000", "CASH", "EQUAL_WEIGHT_PORTFOLIO"]


@dataclass(frozen=True)
class TrackingConfig:
    as_of_date: str = DEFAULT_AS_OF_DATE
    ledger_start_date: str = DEFAULT_AS_OF_DATE
    long_initial_virtual_capital: float = 1_000_000.0
    mid_initial_virtual_capital: float = 1_000_000.0
    short_initial_virtual_capital: float = 1_000_000.0
    currency: str = "CNY"
    fractional_shares_allowed: bool = True
    board_lot_execution_simulated: bool = False
    real_execution_simulated: bool = False
    valuation_price_policy: str = "adjusted_close_then_close"
    fees_model: str = "none"
    slippage_model: str = "none"
    tax_model: str = "none"

    def initial_capital(self, key: str) -> float:
        return float(getattr(self, f"{key}_initial_virtual_capital"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "config_id": "A-SHARE-VIRTUAL-PORTFOLIO-TRACKING-CONFIG",
            "target_version": TARGET_VERSION,
            "as_of_date": self.as_of_date,
            "ledger_start_date": self.ledger_start_date,
            "initial_virtual_capital": {
                "long": self.long_initial_virtual_capital,
                "mid": self.mid_initial_virtual_capital,
                "short": self.short_initial_virtual_capital,
            },
            "currency": self.currency,
            "fractional_shares_allowed": self.fractional_shares_allowed,
            "board_lot_execution_simulated": self.board_lot_execution_simulated,
            "real_execution_simulated": self.real_execution_simulated,
            "valuation_price_policy": self.valuation_price_policy,
            "fees_model": self.fees_model,
            "slippage_model": self.slippage_model,
            "tax_model": self.tax_model,
            "broker_connected": False,
            "real_orders_placed": False,
            **TRACKING_FLAGS,
            "not_order_instruction": True,
            "boundary": dict(TRACKING_BOUNDARY),
            "raw_config": asdict(self),
        }


def validate_tracking_config(config: TrackingConfig) -> list[str]:
    issues: list[str] = []
    if config.as_of_date != config.ledger_start_date:
        issues.append("ledger_start_date must equal as_of_date for initial tracking day")
    for key in PORTFOLIO_KEYS:
        if config.initial_capital(key) <= 0.0:
            issues.append(f"{key}_initial_virtual_capital must be positive")
    if config.valuation_price_policy != "adjusted_close_then_close":
        issues.append("valuation_price_policy must be adjusted_close_then_close")
    if not config.fractional_shares_allowed:
        issues.append("fractional_shares_allowed must be true for v0.7.8 research tracking")
    if config.board_lot_execution_simulated:
        issues.append("board_lot_execution_simulated must be false")
    if config.real_execution_simulated:
        issues.append("real_execution_simulated must be false")
    return issues
