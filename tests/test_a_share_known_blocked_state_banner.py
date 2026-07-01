from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_known_blocked_state_banner_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    banner = operator_data(paths, "known_blocked_state_banner.json")
    assert banner["headline"] == "Owner-readiness is BLOCKED."
    assert banner["owner_operationally_acceptable"] is False
