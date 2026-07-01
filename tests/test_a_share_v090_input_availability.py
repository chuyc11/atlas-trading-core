from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_inputs
from trading_core.equity_owner_v090_rc.input_availability import build_input_availability


def test_v090_input_availability_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_inputs(paths)
    passed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert passed["overall_passed"] is True
    assert passed["source_gate_decision"] == "blocked"
    assert passed["blocks_v090_rc"] is False
    (paths.data_dir / "equity_data_quality" / "a_share_owner_closeout_review_audit.json").unlink()
    failed = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False
    assert "required_inputs_missing" in failed["blocking_reasons"]
