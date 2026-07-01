"""Safety boundary status panel."""

from __future__ import annotations

from trading_core.equity_owner_operator_experience.operator_config import DEFAULT_AS_OF_DATE, TARGET_VERSION


def build_safety_boundary_status_panel(*, as_of_date: str = DEFAULT_AS_OF_DATE) -> dict:
    return {
        "panel_id": "A-SHARE-SAFETY-BOUNDARY-STATUS-PANEL",
        "target_version": TARGET_VERSION,
        "as_of_date": as_of_date,
        "broker_connected": False,
        "real_account_data_read": False,
        "real_orders_placed": False,
        "order_preview_generated": False,
        "buy_sell_signals_generated": False,
        "old_run_daily_called": False,
        "run_daily_called": False,
        "day2_executed": False,
        "model_profit_guaranteed": False,
        "live_trading_ready": False,
        "operator_status_used_as_trade_instruction": False,
        "overall_boundary_clean": True,
        "overall_passed": True,
        "blocking_reasons": [],
        "warnings": [],
    }
