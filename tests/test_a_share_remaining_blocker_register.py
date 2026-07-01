from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_remaining_blocker_register_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    blockers = recovery_evidence_data(paths, "remaining_blocker_register.json")
    assert blockers["register_id"] == "A-SHARE-REMAINING-BLOCKER-REGISTER"
    assert "readiness_score_gap" in blockers["categories"]

