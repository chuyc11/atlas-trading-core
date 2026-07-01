from tests.a_share_v090_rc_test_utils import make_paths, seed_v090_outputs, v090_data


def test_v090_known_blocked_state_blocks_owner_acceptance_not_rc(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    disclosure = v090_data(paths, "v090_known_blocked_state_disclosure.json")
    assert disclosure["owner_readiness_state"] == "blocked"
    assert disclosure["owner_operationally_acceptable"] is False
    assert disclosure["blocks_owner_readiness_acceptance"] is True
    assert disclosure["blocks_v090_rc"] is False
