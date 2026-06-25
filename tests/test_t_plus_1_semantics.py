from trading_core.execution.t_plus_1_semantics import next_execution_date, validate_execution_timeline


def test_t_plus_one_semantics() -> None:
    assert next_execution_date("2024-01-02", "SSE") == "2024-01-03"
    assert next_execution_date("2024-01-05", "SSE") == "2024-01-08"
    assert next_execution_date("2024-09-30", "SSE") == "2024-10-02"
    assert next_execution_date("2024-06-28", "HKEX") == "2024-07-02"
    assert not validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T15:30:00", execution_date="2024-01-02", execution_market="SSE")["accepted"]
    assert not validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T15:30:00", execution_date="2024-01-03", execution_market="SSE", price_date="2024-01-04")["accepted"]
    assert not validate_execution_timeline(signal_date="2024-01-02", generated_at="2024-01-02T14:00:00", execution_date="2024-01-03", execution_market="SSE")["accepted"]

