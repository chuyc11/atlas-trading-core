from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_inputs
from trading_core.equity_owner_v090_rc.audit_sweep import run_audit_sweep


def test_v090_audit_sweep_all_prior_pass(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_inputs(paths)
    sweep = run_audit_sweep(paths=paths, as_of_date=AS_OF_DATE)
    assert sweep["audit_sweep_passed"] is True
    assert sweep["audit_sweep_item_count"] == 10
    assert sweep["failed_audit_sweep_items"] == []
