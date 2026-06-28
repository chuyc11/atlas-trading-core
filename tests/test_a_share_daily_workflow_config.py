from __future__ import annotations

from trading_core.equity_workflows.workflow_config import (
    ALLOWED_MODES,
    FULL_RESEARCH_RUN,
    VALIDATE_EXISTING_ARTIFACTS,
    WorkflowConfig,
    validate_workflow_config,
)


def test_daily_workflow_config_defaults_are_safe() -> None:
    payload = WorkflowConfig().to_dict()

    assert payload["mode"] == VALIDATE_EXISTING_ARTIFACTS
    assert payload["allowed_modes"] == list(ALLOWED_MODES)
    assert payload["allow_public_data_refresh"] is False
    assert payload["call_old_run_daily"] is False
    assert payload["execute_official_forward_dry_run_day2"] is False
    assert payload["broker_enabled"] is False
    assert payload["real_order_enabled"] is False
    assert payload["research_only"] is True
    assert payload["virtual_only"] is True
    assert payload["not_order_instruction"] is True
    assert payload["not_profit_guarantee"] is True
    assert payload["not_live_trading_ready"] is True
    assert payload["build_timestamp_non_strict_idempotency"] is True


def test_daily_workflow_config_validates_modes_and_refresh_scope() -> None:
    assert validate_workflow_config(WorkflowConfig(mode="bad")) == [
        "mode must be one of validate_existing_artifacts, build_from_existing_data, full_research_run"
    ]
    assert validate_workflow_config(WorkflowConfig(mode=FULL_RESEARCH_RUN, allow_public_data_refresh=True)) == []
    assert "allow_public_data_refresh is only valid for full_research_run" in validate_workflow_config(
        WorkflowConfig(allow_public_data_refresh=True)
    )
