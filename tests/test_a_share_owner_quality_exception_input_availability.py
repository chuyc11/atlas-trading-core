from tests.a_share_owner_quality_exception_test_utils import AS_OF_DATE, make_paths, seed_owner_quality_exception_inputs
from trading_core.equity_owner_quality_exceptions.input_availability import build_input_availability


def test_owner_quality_exception_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_inputs(paths)
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["source_gate_decision"] == "blocked"


def test_owner_quality_exception_input_availability_fails_without_gate_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_inputs(paths)
    (paths.data_dir / "equity_data_quality" / "a_share_owner_readiness_gate_audit.json").unlink()
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
