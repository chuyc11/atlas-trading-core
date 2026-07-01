from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_outputs
from trading_core.equity_owner_v090_rc.v090_rc_audit import audit_a_share_owner_v090_rc


def test_v090_rc_audit_fails_closed_when_full_pytest_skipped(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths, skip_full_pytest=True)
    audit = audit_a_share_owner_v090_rc(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is False
    assert "full_pytest_executed" in audit["blocking_reasons"]
