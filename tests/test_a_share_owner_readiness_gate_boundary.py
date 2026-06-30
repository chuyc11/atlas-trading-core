from tests.a_share_owner_readiness_gate_test_utils import gate_data, make_paths, seed_owner_readiness_gate_outputs


def test_owner_readiness_gate_boundary_fields_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_outputs(paths)
    boundary = gate_data(paths, "owner_readiness_gate_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["owner_readiness_gate_used_as_trade_instruction"] is False
