from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_source_review_reads_v095_no_go_result(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    review = final_json(paths, "source_evidence_review")

    assert review["source_artifacts_found"] is True
    assert review["source_audit_passed"] is True
    assert review["future_reevaluation_decision"] == "no_go_additional_evidence_required"
    assert review["ready_for_future_controlled_reevaluation_prep"] is False
    assert review["source_readiness_score"] == 54
    assert review["owner_readiness_state"] == "blocked"
