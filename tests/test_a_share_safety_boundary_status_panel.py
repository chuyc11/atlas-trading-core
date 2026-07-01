from tests.a_share_operator_experience_test_utils import make_paths, operator_data, seed_operator_outputs


def test_safety_boundary_status_panel_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    panel = operator_data(paths, "safety_boundary_status_panel.json")
    assert panel["overall_boundary_clean"] is True
    assert panel["broker_connected"] is False
    assert panel["real_orders_placed"] is False
