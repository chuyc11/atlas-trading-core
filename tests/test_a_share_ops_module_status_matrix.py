from trading_core.equity_ops_center.module_status_matrix import build_ops_module_status_matrix


def test_ops_module_status_matrix_aggregation():
    availability = {"modules": [{"module_id": "data_refresh", "available": True, "audit_passed": True, "blocking_reasons": [], "warning_count": 1, "boundary_passed": True, "source_trace_path": "x", "summary_path": "y"}]}
    matrix = build_ops_module_status_matrix(as_of_date="2026-06-26", availability=availability)
    assert matrix["rows"][0]["status"] == "passed_with_warnings"
    assert matrix["required_modules_passed"] is True
