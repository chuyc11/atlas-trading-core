from tests.a_share_final_closeout_test_utils import final_json, seed_v095_and_build_v096


def test_final_closeout_boundary_blocks_gate_broker_orders_and_signals(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    boundary = final_json(paths, "final_closeout_boundary_check")

    assert boundary["overall_passed"] is True
    assert boundary["selected_branch"] == "final_not_ready_closeout"
    assert boundary["data_refresh_run"] is False
    assert boundary["research_pipeline_rerun_run"] is False
    assert boundary["build_from_existing_data_run"] is False
    assert boundary["owner_readiness_gate_rerun"] is False
    assert boundary["controlled_gate_reevaluation_run"] is False
    assert boundary["new_gate_score_generated"] is False
    assert boundary["new_gate_decision_generated"] is False
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False
    assert boundary["buy_sell_signals_generated"] is False
    assert boundary["final_closeout_used_as_trade_instruction"] is False
    assert boundary["protected_paths_untouched"] is True
