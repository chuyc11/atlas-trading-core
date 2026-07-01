from tests.a_share_operator_experience_test_utils import AS_OF_DATE, make_paths, operator_data, seed_operator_outputs
from trading_core.equity_owner_operator_experience.operator_experience_audit import audit_a_share_owner_operator_experience


def test_operator_experience_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    audit = audit_a_share_owner_operator_experience(paths=paths)
    assert audit["overall_passed"] is True
    (paths.data_dir / "equity_owner_operator_experience" / "daily" / AS_OF_DATE / "operator_action_menu.json").unlink()
    failed = audit_a_share_owner_operator_experience(paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]
