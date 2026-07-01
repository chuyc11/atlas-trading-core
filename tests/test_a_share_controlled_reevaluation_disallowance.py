from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_disallowance_record_contains_v095_no_go_reasons(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    record = final_json(paths, "controlled_reevaluation_disallowance_record")

    assert record["controlled_reevaluation_disallowed"] is True
    assert record["controlled_reevaluation_executed"] is False
    assert record["owner_readiness_gate_rerun"] is False
    assert record["new_gate_score_generated"] is False
    assert "future_reevaluation_decision=no_go_additional_evidence_required" in record["disallowance_reasons"]
    assert "controlled_reevaluation_precheck_status=not_ready" in record["disallowance_reasons"]
    assert record["manual_override_allowed"] is False
    assert record["threshold_lowered"] is False
    assert record["waiver_applied"] is False
