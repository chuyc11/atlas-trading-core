from trading_core.equity_owner_monitoring.alert_rules import build_alert_rule_config


def test_alert_rule_config_contains_required_rules():
    config = build_alert_rule_config(as_of_date="2026-06-26")
    rule_ids = {row["rule_id"] for row in config["rules"]}
    assert "BOUNDARY_VIOLATION" in rule_ids
    assert "TREND_ANALYSIS_INSUFFICIENT_HISTORY" in rule_ids
