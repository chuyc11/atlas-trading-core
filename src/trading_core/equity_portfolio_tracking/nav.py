"""NAV and holdings snapshot calculations for virtual tracking."""

from __future__ import annotations

from typing import Any

from trading_core.equity_portfolio_tracking.tracking_config import PORTFOLIO_HORIZONS, PORTFOLIO_IDS, TRACKING_BOUNDARY, TRACKING_FLAGS, TrackingConfig


def build_holdings_snapshot(
    *,
    portfolio_key: str,
    ledger: list[dict[str, Any]],
    source_rows: list[dict[str, Any]],
    config: TrackingConfig,
) -> dict[str, Any]:
    source_by_symbol = {str(row.get("symbol")): row for row in source_rows}
    nav_record = calculate_nav(portfolio_key=portfolio_key, ledger=ledger, config=config)
    holdings = []
    for record in ledger:
        symbol = str(record.get("symbol"))
        source = source_by_symbol.get(symbol, {})
        market_value = float(record.get("virtual_shares") or 0.0) * float(record.get("mark_price") or 0.0)
        holdings.append(
            {
                "symbol": symbol,
                "name": record.get("name", ""),
                "portfolio_horizon": record.get("portfolio_horizon") or PORTFOLIO_HORIZONS[portfolio_key],
                "virtual_shares": float(record.get("virtual_shares") or 0.0),
                "entry_price": float(record.get("entry_price") or 0.0),
                "mark_price": float(record.get("mark_price") or 0.0),
                "target_weight": float(record.get("target_weight") or 0.0),
                "actual_weight": market_value / nav_record["portfolio_nav"] if nav_record["portfolio_nav"] else 0.0,
                "virtual_position_value": market_value,
                "unrealized_pnl": market_value - float(record.get("virtual_position_value") or 0.0),
                "unrealized_return": _safe_return(market_value, float(record.get("virtual_position_value") or 0.0)),
                "candidate_source": record.get("candidate_source", ""),
                "score_snapshot": record.get("score_snapshot", {}),
                "risk_notes": record.get("risk_notes", []),
                "industry": source.get("industry") or source.get("industry_level_1") or "",
                "industry_level_1": source.get("industry_level_1", ""),
                "industry_level_2": source.get("industry_level_2", ""),
                **TRACKING_FLAGS,
            }
        )
    return {
        "snapshot_id": f"{portfolio_key.upper()}-VIRTUAL-HOLDINGS-SNAPSHOT",
        "target_version": nav_record["target_version"],
        "as_of_date": config.as_of_date,
        "portfolio_id": PORTFOLIO_IDS[portfolio_key],
        "portfolio_horizon": PORTFOLIO_HORIZONS[portfolio_key],
        "holdings": holdings,
        "metrics": nav_record,
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
    }


def calculate_nav(*, portfolio_key: str, ledger: list[dict[str, Any]], config: TrackingConfig) -> dict[str, Any]:
    initial_capital = config.initial_capital(portfolio_key)
    holdings_market_value = round(sum(float(row.get("virtual_shares") or 0.0) * float(row.get("mark_price") or 0.0) for row in ledger), 6)
    cash_balance = round(initial_capital - sum(float(row.get("virtual_position_value") or 0.0) for row in ledger), 6)
    portfolio_nav = round(cash_balance + holdings_market_value, 6)
    weights = [float(row.get("target_weight") or 0.0) for row in ledger]
    actual_weights = [
        (float(row.get("virtual_shares") or 0.0) * float(row.get("mark_price") or 0.0)) / portfolio_nav if portfolio_nav else 0.0
        for row in ledger
    ]
    return {
        "target_version": "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger",
        "as_of_date": config.as_of_date,
        "portfolio_id": PORTFOLIO_IDS[portfolio_key],
        "portfolio_horizon": PORTFOLIO_HORIZONS[portfolio_key],
        "initial_virtual_capital": initial_capital,
        "portfolio_nav": portfolio_nav,
        "cash_balance": cash_balance,
        "holdings_market_value": holdings_market_value,
        "gross_exposure": sum(abs(weight) for weight in actual_weights),
        "net_exposure": sum(actual_weights),
        "holding_count": len(ledger),
        "weight_sum": sum(weights),
        "actual_weight_sum": sum(actual_weights),
        "max_single_weight": max(weights or [0.0]),
        "first_day_initialization": True,
        "performance_not_yet_observed": True,
        **TRACKING_FLAGS,
    }


def build_nav_snapshot(config: TrackingConfig, nav_records: dict[str, dict[str, Any]]) -> dict[str, Any]:
    return {
        "snapshot_id": "A-SHARE-VIRTUAL-PORTFOLIO-NAV-SNAPSHOT",
        "target_version": "v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger",
        "as_of_date": config.as_of_date,
        "portfolios": nav_records,
        **TRACKING_FLAGS,
        "boundary": dict(TRACKING_BOUNDARY),
    }


def _safe_return(current: float, cost: float) -> float:
    if cost == 0.0:
        return 0.0
    return current / cost - 1.0
