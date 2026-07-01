from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_unresolved_blocker_digest_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    digest = operator_data(paths, "unresolved_blocker_digest.json")
    assert digest["unresolved_blocker_count"] == 7
    assert digest["blockers_that_block_v090_rc"] == 0
