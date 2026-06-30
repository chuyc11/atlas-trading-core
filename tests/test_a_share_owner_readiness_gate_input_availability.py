from tests.a_share_owner_readiness_gate_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_gate_inputs
from trading_core.equity_owner_readiness_gate.input_availability import build_input_availability


def test_owner_readiness_gate_input_availability_passes(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_inputs(paths)
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is True
    assert result["owner_daily_pack_history_audit_passed"] is True


def test_owner_readiness_gate_input_availability_fails_without_history_audit(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_inputs(paths)
    (paths.data_dir / "equity_data_quality" / "a_share_owner_daily_pack_history_audit.json").unlink()
    result = build_input_availability(paths=paths, as_of_date=AS_OF_DATE)
    assert result["overall_passed"] is False
    assert "owner_daily_pack_history_audit_not_passed" in result["blocking_reasons"]
