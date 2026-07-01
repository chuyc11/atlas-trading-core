from tests.a_share_v090_rc_test_utils import make_paths, seed_v090_outputs, v090_data


def test_v090_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    trace = v090_data(paths, "v090_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert all(row["sha256"] for row in trace["source_artifacts"] if row["required"])
