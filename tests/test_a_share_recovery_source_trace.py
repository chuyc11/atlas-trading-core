from pathlib import Path

from trading_core.equity_data_quality.common import sha256_file
from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_source_trace_complete_and_hashes_match(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    trace = recovery_data(paths, "recovery_source_trace.json")
    assert trace["source_trace_complete"] is True
    for row in trace["source_artifacts"]:
        path = Path(row["path"])
        assert path.exists()
        assert row["sha256"] == sha256_file(path)
