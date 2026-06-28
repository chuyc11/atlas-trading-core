"""Paper ledger construction for research-only virtual portfolios."""

from __future__ import annotations

import json
from typing import Any

from trading_core.equity_portfolio_tracking.tracking_config import LEDGER_FLAGS, PORTFOLIO_HORIZONS, PORTFOLIO_IDS, TrackingConfig
from trading_core.equity_portfolio_tracking.tracking_inputs import TrackingInputs
from trading_core.equity_portfolio_tracking.valuation import ValuationPrice
from trading_core.system.common import relative


def build_paper_ledger(
    *,
    inputs: TrackingInputs,
    config: TrackingConfig,
    portfolio_key: str,
    valuation_prices: dict[str, ValuationPrice],
    created_at: str,
) -> list[dict[str, Any]]:
    rows = inputs.portfolios[portfolio_key]
    initial_capital = config.initial_capital(portfolio_key)
    nav = initial_capital
    final_cash = initial_capital - sum(initial_capital * float(row.get("target_weight") or 0.0) for row in rows)
    records = []
    for row in rows:
        symbol = str(row.get("symbol"))
        valuation = valuation_prices[symbol]
        target_weight = float(row.get("target_weight") or 0.0)
        position_value = initial_capital * target_weight
        virtual_shares = position_value / valuation.price
        records.append(
            {
                "ledger_id": f"{portfolio_key}_paper_ledger",
                "as_of_date": inputs.as_of_date,
                "ledger_start_date": config.ledger_start_date,
                "portfolio_id": PORTFOLIO_IDS[portfolio_key],
                "portfolio_horizon": str(row.get("portfolio_horizon") or PORTFOLIO_HORIZONS[portfolio_key]),
                "record_type": "virtual_initial_position",
                "symbol": symbol,
                "name": row.get("name", ""),
                "virtual_position_value": position_value,
                "virtual_shares": virtual_shares,
                "entry_price": valuation.price,
                "mark_price": valuation.price,
                "valuation_price_record": valuation.to_dict(),
                "target_weight": target_weight,
                "actual_weight": position_value / nav if nav else 0.0,
                "cash_effect": 0.0,
                "virtual_cash_balance_after": final_cash,
                "unrealized_pnl": 0.0,
                "unrealized_return": 0.0,
                "candidate_source": row.get("candidate_source", ""),
                "score_snapshot": _score_snapshot(row),
                "risk_notes": _listish(row.get("risk_notes")),
                "source_virtual_portfolio_path": relative(inputs.portfolio_dir / f"{portfolio_key}_virtual_portfolio.json", inputs.portfolio_dir.parents[3]),
                "fractional_shares_allowed": config.fractional_shares_allowed,
                "board_lot_execution_simulated": config.board_lot_execution_simulated,
                "real_execution_simulated": config.real_execution_simulated,
                "created_at": created_at,
                **LEDGER_FLAGS,
            }
        )
    return records


def _score_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "LongScore",
        "MidScore",
        "ShortScore",
        "RiskScore",
        "LiquidityScore",
        "IndustryScore",
        "FundamentalScore",
        "CompositeOpportunityScore",
        "candidate_rank",
        "weight_rank",
    ]
    return {key: _value(row.get(key)) for key in keys if key in row}


def _value(value: Any) -> Any:
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return value


def _listish(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value in (None, ""):
        return []
    if isinstance(value, str):
        text = value.strip()
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except json.JSONDecodeError:
                return [text]
        return [text]
    return [str(value)]
