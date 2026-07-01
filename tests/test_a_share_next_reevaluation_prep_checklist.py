from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_next_reevaluation_prep_defaults_false(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    checklist = recovery_evidence_data(paths, "next_reevaluation_prep_checklist.json")
    assert checklist["ready_for_evidence_backed_gate_prep"] is False
    assert checklist["threshold_unchanged"] is True
    assert checklist["waiver_not_used"] is True

