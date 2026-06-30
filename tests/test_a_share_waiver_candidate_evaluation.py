from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_waiver_candidate_evaluation_blocks_auto_waiver(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    evaluation = exception_data(paths, "waiver_candidate_evaluation.json")
    assert evaluation["auto_waiver_allowed"] is False
    assert evaluation["waiver_changes_gate_decision"] is False
