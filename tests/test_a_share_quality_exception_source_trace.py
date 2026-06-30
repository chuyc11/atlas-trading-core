from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_quality_exception_source_trace_complete_and_hashes_present(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    trace = exception_data(paths, "quality_exception_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert all(row["sha256"] for row in trace["source_artifacts"] if row["required"])
