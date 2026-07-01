from tests.a_share_v0820_test_utils import AS_OF_DATE, make_paths, seed_v0820_outputs
from trading_core.equity_owner_v0820_gate_outcome.v0820_outcome_audit import audit_a_share_owner_v0820_gate_outcome


def test_v0820_outcome_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_outputs(paths)
    passed = audit_a_share_owner_v0820_gate_outcome(as_of_date=AS_OF_DATE, paths=paths)
    assert passed["overall_passed"] is True
    assert passed["outcome_checks"]["selected_branch"] == "final_blocked_closeout"
    assert passed["outcome_checks"]["final_blocked_closeout_generated"] is True
    (paths.data_dir / "equity_owner_v0820_gate_outcome" / "daily" / AS_OF_DATE / "v0820_manifest.json").unlink()
    failed = audit_a_share_owner_v0820_gate_outcome(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]

