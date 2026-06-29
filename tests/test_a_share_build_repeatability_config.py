import pytest

from trading_core.equity_build_repeatability.repeatability_config import (
    RUN_REPEAT_BUILD_FROM_EXISTING_DATA,
    RepeatabilityConfig,
    validate_repeatability_config,
)


def test_repeatability_config_defaults():
    payload = RepeatabilityConfig().to_dict()
    assert payload["workflow_mode"] == "build_from_existing_data"
    assert payload["mode"] == RUN_REPEAT_BUILD_FROM_EXISTING_DATA
    assert payload["allow_business_output_drift"] is False
    assert payload["allow_preexisting_protected_paths"] is True


def test_repeatability_config_rejects_broker():
    assert "broker is not allowed in repeatability checks" in validate_repeatability_config(
        RepeatabilityConfig(allow_broker=True)
    )

