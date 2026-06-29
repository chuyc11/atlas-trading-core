from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_owner_monitoring.monitoring_source_trace import build_monitoring_source_trace


def test_monitoring_source_trace_blocks_forbidden_paths(tmp_path):
    paths = make_paths(tmp_path)
    trace = build_monitoring_source_trace(paths=paths, as_of_date=AS_OF_DATE, generated_at="now", source_paths=[paths.data_dir / "orders" / "orders-2026-06-26.jsonl"], history_paths=[], output_paths=[], alert_rule_decisions=[], warning_carry_forward_decisions=[])
    assert trace["source_trace_complete"] is False
    assert trace["forbidden_path_hits"]
