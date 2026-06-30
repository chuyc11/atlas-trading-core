from tests.a_share_controlled_gate_reevaluation_test_utils import controlled_data, make_paths, seed_controlled_gate_reevaluation_outputs


def test_controlled_gate_reevaluation_boundary_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_outputs(paths)
    boundary = controlled_data(paths, "controlled_reevaluation_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["gate_reevaluation_executed"] is False
    assert boundary["broker_connected"] is False
    assert boundary["controlled_reevaluation_used_as_trade_instruction"] is False

