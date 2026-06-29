from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.dashboard_source_trace import build_dashboard_source_trace


def test_source_trace_rejects_forbidden_paths(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    trace = build_dashboard_source_trace(paths=paths, as_of_date=AS_OF_DATE, resolved_as_of_date=AS_OF_DATE, generated_at="now", source_paths=[paths.data_dir / "orders" / "x.json"], output_paths=[], warnings=[])
    assert trace["source_trace_complete"] is False
    assert trace["forbidden_path_hits"]
