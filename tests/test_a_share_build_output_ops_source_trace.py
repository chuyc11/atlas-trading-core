from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs
from trading_core.equity_build_output_ops_refresh.input_availability import load_json


def test_build_output_ops_source_trace_complete_and_hashes_match(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    trace = load_json(paths.data_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE / "build_output_ops_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert all(entry["sha256"] for entry in trace["entries"] if entry["required"])

