from tests.a_share_evidence_backed_prep_test_utils import AS_OF_DATE, make_paths, seed_evidence_backed_prep_outputs, prep_data


def test_evidence_backed_prep_source_trace_complete_and_hashed(tmp_path):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_outputs(paths)
    trace = prep_data(paths, "evidence_backed_prep_source_trace.json")
    assert trace["source_trace_complete"] is True
    assert trace["source_artifacts"]
    assert all(row["sha256"] for row in trace["source_artifacts"] if row["required"])

