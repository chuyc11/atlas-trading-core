from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_current_day_builds.gated_build_source_trace import build_gated_build_source_trace


def test_gated_build_source_trace_blocks_forbidden_paths(tmp_path):
    paths = make_paths(tmp_path)
    path = paths.data_dir / "broker" / "x.json"
    write_json(path, {})
    trace = build_gated_build_source_trace(paths=paths, as_of_date=AS_OF_DATE, source_artifacts={"bad": path}, output_artifacts={})
    assert trace["source_trace_complete"] is False
    assert trace["forbidden_path_hits"]

