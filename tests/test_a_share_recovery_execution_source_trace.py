from pathlib import Path

from trading_core.equity_data_quality.common import sha256_file
from tests.a_share_recovery_execution_test_utils import make_paths, execution_data, seed_recovery_execution_outputs


def test_recovery_execution_source_trace_complete_and_hashes_match(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_execution_outputs(paths)
    trace = execution_data(paths, "recovery_execution_source_trace.json")
    assert trace["source_trace_complete"] is True
    for row in trace["source_artifacts"]:
        path = Path(row["path"])
        assert path.exists()
        assert row["sha256"] == sha256_file(path)
