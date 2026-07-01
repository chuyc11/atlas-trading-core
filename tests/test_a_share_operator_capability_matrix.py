from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_operator_capability_matrix_disallows_forbidden(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    matrix = operator_data(paths, "operator_capability_matrix.json")
    rows = {row["capability_id"]: row for row in matrix["capabilities"]}
    assert rows["view_rc_report"]["allowed"] is True
    assert rows["connect_broker"]["allowed"] is False
    assert matrix["forbidden_capabilities_disallowed"] is True
