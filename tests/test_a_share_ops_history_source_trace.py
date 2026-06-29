from tests.a_share_ops_history_test_utils import build_ops_history_artifacts
from tests.a_share_owner_dashboard_test_utils import make_paths
from trading_core.equity_ops_history.input_availability import load_json
from trading_core.equity_ops_history.ops_history_config import ops_history_artifact_paths


def test_ops_history_source_trace_is_complete(tmp_path):
    paths = make_paths(tmp_path)
    build_ops_history_artifacts(paths)
    trace = load_json(ops_history_artifact_paths(paths, "2026-06-26")["ops_history_source_trace"])
    assert trace["source_trace_complete"] is True
    assert trace["forbidden_path_hits"] == []

