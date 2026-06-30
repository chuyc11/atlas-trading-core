from tests.a_share_owner_readiness_recovery_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_recovery_inputs
from trading_core.equity_owner_readiness_recovery.input_availability import build_input_availability


def test_owner_readiness_recovery_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_inputs(paths)
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["quality_exception_workflow_audit_passed"] is True
    assert result["source_gate_decision"] == "blocked"


def test_owner_readiness_recovery_input_availability_fails_without_quality_exception_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_recovery_inputs(paths)
    (paths.data_dir / "equity_data_quality" / "a_share_owner_quality_exception_workflow_audit.json").unlink()
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
