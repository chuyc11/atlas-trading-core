from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v38_execution_microstructure_does_not_emit_signal(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v38")
    execution = component_json(paths, "v38", "v38_execution_path_edge_case_result")

    assert result["execution_path_edge_case_result_generated"] is True
    assert result["execution_edge_fabricated"] is False
    assert result["account_apply_trade_bypass_absent"] is True
    assert result["microstructure_validation_generates_trade_signal"] is False
    assert execution["simulated_order_remains_simulated"] is True
