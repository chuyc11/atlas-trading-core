from tests.a_share_owner_quality_exception_test_utils import exception_data, make_paths, seed_owner_quality_exception_outputs


def test_threshold_failure_explanation_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    explanation = exception_data(paths, "threshold_failure_explanation.json")
    assert explanation["blocked_gate_decision_preserved"] is True
    assert explanation["not_trade_instruction"] is True
