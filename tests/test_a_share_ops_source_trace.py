from tests.a_share_owner_dashboard_test_utils import make_paths
from trading_core.equity_ops_center.ops_source_trace import build_ops_source_trace, forbidden_source_path_hits


def test_ops_source_trace_complete_and_blocks_forbidden_paths(tmp_path):
    paths = make_paths(tmp_path)
    source = paths.project_root / "data" / "source.json"
    source.write_text("{}", encoding="utf-8")
    trace = build_ops_source_trace(paths=paths, as_of_date="2026-06-26", generated_at="now", source_paths={"source": source}, output_paths={}, command_policy_decisions={})
    assert trace["source_trace_complete"] is True
    assert forbidden_source_path_hits([{"path": "data/orders/x.json"}])
