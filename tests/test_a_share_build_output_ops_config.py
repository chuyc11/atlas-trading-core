from trading_core.equity_build_output_ops_refresh.build_output_ops_config import (
    ALLOWED_MODES,
    BUILD_REFRESH,
    BuildOutputOpsRefreshConfig,
    validate_config,
)


def test_build_output_ops_config_defaults():
    config = BuildOutputOpsRefreshConfig()
    payload = config.to_dict()
    assert payload["mode"] == BUILD_REFRESH
    assert payload["source_workflow_mode"] == "build_from_existing_data"
    assert payload["rerun_build_from_existing_data"] is False
    assert payload["execute_remediation_actions"] is False
    assert payload["send_external_notifications"] is False
    assert validate_config(config) == []
    assert BUILD_REFRESH in ALLOWED_MODES

