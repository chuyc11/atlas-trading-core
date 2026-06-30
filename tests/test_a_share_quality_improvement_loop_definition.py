from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_quality_improvement_loop_definition_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    loop = recovery_data(paths, "quality_improvement_loop_definition.json")
    assert loop["executes_audit_only_verification_now"] is False
    assert loop["executes_gate_reevaluation_now"] is False
    assert loop["steps"]
