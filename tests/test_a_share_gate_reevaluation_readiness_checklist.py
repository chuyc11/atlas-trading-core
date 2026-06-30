from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_gate_reevaluation_readiness_checklist_defaults_not_ready(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    checklist = recovery_data(paths, "gate_reevaluation_readiness_checklist.json")
    assert checklist["ready_for_future_gate_reevaluation"] is False
    assert checklist["no_threshold_lowering"] is True
    assert checklist["no_auto_waiver"] is True
