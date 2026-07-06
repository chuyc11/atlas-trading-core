from a_share_v3x_release_test_utils import build_through, component_json, make_v3x_paths


def test_v39_docs_and_handoff_do_not_include_trading_steps(tmp_path):
    paths = make_v3x_paths(tmp_path)
    result = build_through(paths, "v39")
    docs = component_json(paths, "v39", "v39_final_documentation_result")

    assert result["v38_baseline_verified"] is True
    assert result["final_documentation_generated"] is True
    assert result["owner_handoff_package_generated"] is True
    assert result["handoff_includes_broker_setup"] is False
    assert result["handoff_includes_real_account_steps"] is False
    assert result["handoff_includes_trading_instruction"] is False
    assert docs["docs_language"] == "zh-CN-owner-facing"
