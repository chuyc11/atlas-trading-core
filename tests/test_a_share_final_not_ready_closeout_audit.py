from tests.a_share_final_closeout_test_utils import AS_OF_DATE, seed_v095_and_build_v096
from trading_core.equity_readiness_final_closeout import audit_a_share_final_not_ready_closeout


def test_final_not_ready_closeout_audit_passes_and_preserves_policy(tmp_path):
    paths, _ = seed_v095_and_build_v096(tmp_path)
    audit = audit_a_share_final_not_ready_closeout(paths=paths, as_of_date=AS_OF_DATE)

    assert audit["overall_passed"] is True
    assert audit["blocking_reasons"] == []
    assert audit["source_checks"]["v095_baseline_verified"] is True
    assert audit["branch_checks"]["selected_branch"] == "final_not_ready_closeout"
    assert audit["branch_checks"]["controlled_reevaluation_allowed"] is False
    assert audit["boundary"]["owner_readiness_gate_rerun"] is False
    assert audit["boundary"]["broker_connected"] is False
    assert audit["test_policy"]["full_pytest_run"] is False
