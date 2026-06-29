from trading_core.equity_ops_history.module_reliability import build_ops_module_reliability_baseline


def test_ops_module_reliability_rates_are_null_when_history_insufficient():
    baseline = build_ops_module_reliability_baseline(as_of_date="2026-06-26", module_matrix={"rows": [{"module_id": "ops_center", "status": "passed"}]}, records=[{}], minimum_required_observations=5)
    assert baseline["modules"]
    assert all(row["reliability_rate"] is None for row in baseline["modules"])

