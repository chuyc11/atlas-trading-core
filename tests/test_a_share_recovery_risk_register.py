from tests.a_share_owner_readiness_recovery_test_utils import make_paths, recovery_data, seed_owner_readiness_recovery_outputs


def test_a_share_recovery_risk_register_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_outputs(paths)
    register = recovery_data(paths, "recovery_risk_register.json")
    assert register["risks"]
    assert all(item["owner_visible"] is True for item in register["risks"])
