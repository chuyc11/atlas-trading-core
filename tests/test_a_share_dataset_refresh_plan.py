from __future__ import annotations

from trading_core.equity_data_refresh.dataset_refresh_plan import build_dataset_refresh_plan


def test_dataset_refresh_plan_validate_existing() -> None:
    plan = build_dataset_refresh_plan(as_of_date="2026-06-26", mode="validate_existing_data")
    assert all(row["refresh_action"] == "validate_existing" for row in plan["datasets"])
