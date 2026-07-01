from tests.a_share_operator_experience_test_utils import make_paths, seed_operator_inputs
from trading_core.equity_owner_operator_experience.input_availability import build_input_availability


def test_operator_input_availability_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_inputs(paths)
    passed = build_input_availability(paths=paths)
    assert passed["overall_passed"] is True
    (paths.data_dir / "equity_data_quality" / "a_share_owner_v090_rc_audit.json").unlink()
    failed = build_input_availability(paths=paths)
    assert failed["overall_passed"] is False
    assert "v090_rc_audit" in failed["blocking_reasons"]
