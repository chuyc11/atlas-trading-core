from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_operator_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    trace = operator_data(paths, "operator_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert trace["output_artifacts"]
