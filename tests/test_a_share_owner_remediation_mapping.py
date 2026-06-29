from trading_core.equity_owner_remediation.remediation_mapping import build_alert_remediation_map, build_blocking_remediation_map, build_warning_remediation_map, mapping_for_code


def test_known_warning_mapping():
    item = mapping_for_code("daily_basic:required_field_all_null")
    assert item["category"] == "schema_issue"
    assert item["severity"] == "known_non_blocking"


def test_blocking_and_alert_maps_include_required_codes():
    blocking = build_blocking_remediation_map([])
    alerts = build_alert_remediation_map([])
    warnings = build_warning_remediation_map([])
    assert any(item["issue_code"] == "DATA_REFRESH_FAILURE" for item in blocking["items"])
    assert any(item["issue_code"] == "PROVIDER_HEALTH_DEGRADED" for item in alerts["items"])
    assert any(item["issue_code"] == "trading_calendar:exchange_level_calendar_collapsed_to_trade_date" for item in warnings["items"])
