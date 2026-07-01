from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_operator_action_menu_only_safe_actions(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    menu = operator_data(paths, "operator_action_menu.json")
    assert menu["forbidden_operator_actions_present"] is False
    assert all(row["allowed"] is True for row in menu["actions"])
