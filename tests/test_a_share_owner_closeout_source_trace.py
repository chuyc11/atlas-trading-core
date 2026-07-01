from tests.a_share_owner_closeout_review_test_utils import make_paths, seed_closeout_outputs, closeout_data


def test_closeout_source_trace_complete_and_hashed(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    trace = closeout_data(paths, "closeout_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert all(row["sha256"] for row in trace["source_artifacts"] if row["required"])
