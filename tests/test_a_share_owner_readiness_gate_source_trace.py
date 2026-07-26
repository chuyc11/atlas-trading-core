from tests.a_share_owner_readiness_gate_test_utils import gate_data, make_paths, seed_owner_readiness_gate_outputs


def test_owner_readiness_gate_source_trace_complete_and_hashes_present(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_outputs(paths)
    trace = gate_data(paths, "owner_readiness_gate_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert all(row["sha256"] for row in trace["source_artifacts"] if row["required"])
    assert trace["output_artifacts"]
