from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_recovery_evidence_source_trace_complete(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    trace = recovery_evidence_data(paths, "recovery_evidence_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert trace["output_artifacts"]

