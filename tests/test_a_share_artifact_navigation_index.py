from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_artifact_navigation_index_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    index = operator_data(paths, "artifact_navigation_index.json")
    assert "current_status" in index["navigation_groups"]
    assert "v0.9.0_rc" in index["navigation_groups"]
