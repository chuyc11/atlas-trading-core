from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_evidence_gap_register_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    gaps = recovery_evidence_data(paths, "evidence_gap_register.json")
    assert gaps["register_id"] == "A-SHARE-EVIDENCE-GAP-REGISTER"
    assert gaps["gap_count"] >= 1
    assert all(item["blocks_next_reevaluation_prep"] for item in gaps["items"])

