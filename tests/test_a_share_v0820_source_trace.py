from tests.a_share_v0820_test_utils import make_paths, seed_v0820_outputs, v0820_data


def test_v0820_source_trace_complete_and_hashed(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_outputs(paths)
    trace = v0820_data(paths, "v0820_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert all(row["sha256"] for row in trace["source_artifacts"] if row["required"])

