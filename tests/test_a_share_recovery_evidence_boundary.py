from tests.a_share_recovery_evidence_test_utils import recovery_evidence_data, make_paths, seed_recovery_evidence_outputs


def test_recovery_evidence_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    boundary = recovery_evidence_data(paths, "recovery_evidence_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["rerun_owner_readiness_gate"] is False
    assert boundary["broker_connected"] is False
    assert boundary["recovery_evidence_used_as_trade_instruction"] is False

