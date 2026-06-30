from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, controlled_data, make_paths, seed_controlled_gate_reevaluation_outputs


def test_controlled_gate_reevaluation_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_outputs(paths)
    trace = controlled_data(paths, "controlled_reevaluation_source_trace.json", AS_OF_DATE)
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert trace["output_artifacts"]

