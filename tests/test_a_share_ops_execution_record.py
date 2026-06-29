from trading_core.equity_ops_center.ops_execution_record import build_ops_execution_record


def test_ops_execution_record_default_empty_commands():
    record = build_ops_execution_record(as_of_date="2026-06-26", mode="aggregate_existing_ops_artifacts")
    assert record["commands_executed"] == []
    assert record["aggregate_existing_artifacts_only"] is True
    assert record["safe_validation_chain_run"] is False
