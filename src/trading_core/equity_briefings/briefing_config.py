"""Configuration for v0.7.7 A-share daily stock selection briefing."""

from __future__ import annotations


TARGET_VERSION = "v0.7.7-a-share-daily-stock-selection-briefing"
RECOMMENDED_NEXT_VERSION = "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger"
REMEDIATION_VERSION = "v0.7.7.1-a-share-daily-stock-selection-briefing-remediation"
DEFAULT_AS_OF_DATE = "2026-06-26"

BRIEFING_BOUNDARY = {
    "briefing_only": True,
    "scores_regenerated": False,
    "candidates_regenerated": False,
    "virtual_portfolios_regenerated": False,
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

BRIEFING_FILES = {
    "daily_stock_selection_briefing": "daily_stock_selection_briefing.json",
    "briefing_manifest": "briefing_manifest.json",
    "briefing_source_trace": "briefing_source_trace.json",
    "briefing_boundary_check": "briefing_boundary_check.json",
}

BRIEFING_REPORTS = {
    "daily_stock_selection_briefing_report": "DAILY_STOCK_SELECTION_BRIEFING.md",
    "briefing_source_trace_report": "BRIEFING_SOURCE_TRACE.md",
}

REQUIRED_SECTION_KEYS = {
    "executive_summary": "executive_summary",
    "long_candidates_top10": "long_candidates_top10",
    "mid_candidates_top10": "mid_candidates_top10",
    "short_candidates_top10": "short_candidates_top10",
    "multi_horizon_candidates": "multi_horizon_candidates_top10",
    "risk_downgraded_candidates": "risk_downgraded_summary",
    "virtual_portfolio_summary": "virtual_portfolios",
    "industry_exposure_summary": "industry_exposure_summary",
    "risk_liquidity_summary": "risk_liquidity_summary",
    "audit_status": "audit_status",
    "do_not_misread": "do_not_misread",
    "next_tracking_actions": "next_tracking_actions",
}

SOURCE_TRACE_SECTION_KEYS = [
    "executive_summary",
    "long_candidates_top10",
    "mid_candidates_top10",
    "short_candidates_top10",
    "multi_horizon_candidates",
    "risk_downgraded_candidates",
    "virtual_portfolio_summary",
    "industry_exposure_summary",
    "risk_liquidity_summary",
    "audit_status",
    "do_not_misread",
    "next_tracking_actions",
]

FORBIDDEN_BRIEFING_WORDING = [
    "保证盈利",
    "一定赚钱",
    "必涨",
    "买入建议",
    "卖出建议",
    "建仓",
    "加仓",
    "减仓",
    "下单",
    "实盘就绪",
    "连接券商",
    "真实订单",
    "guaranteed profit",
    "buy signal",
    "sell signal",
    "order instruction",
    "live trading ready",
]

NEGATIVE_CONTEXT_ALLOWLIST = [
    "不是买入建议",
    "不是卖出建议",
    "不是下单",
    "没有下单",
    "不得下单",
    "不涉及下单",
    "不是建仓",
    "不得建仓",
    "不是加仓",
    "不得加仓",
    "不是减仓",
    "不得减仓",
    "没有真实订单",
    "不生成真实订单",
    "不是真实订单",
    "无真实订单",
    "没有 broker 连接",
    "未连接 broker",
    "不连接 broker",
    "不是保证盈利",
    "不保证盈利",
    "不代表确定盈利",
    "不是实盘就绪",
    "不具备实盘就绪",
    "not a buy signal",
    "not a sell signal",
    "not an order instruction",
    "no real orders",
    "not live trading ready",
    "not guaranteed profit",
]
