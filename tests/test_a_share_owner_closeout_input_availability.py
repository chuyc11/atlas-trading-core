from tests.a_share_owner_closeout_review_test_utils import AS_OF_DATE, make_paths, seed_closeout_inputs
from trading_core.equity_owner_closeout_review.input_availability import build_input_availability


def test_closeout_input_availability_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_inputs(paths)
    passed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert passed["overall_passed"] is True
    assert passed["selected_v0820_branch"] == "final_blocked_closeout"
    assert passed["score_gap"] == passed["minimum_owner_readiness_score"] - passed["previous_readiness_score"]
    (paths.data_dir / "equity_data_quality" / "a_share_owner_v0820_gate_outcome_audit.json").unlink()
    failed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False
    assert "required_inputs_missing" in failed["blocking_reasons"]
