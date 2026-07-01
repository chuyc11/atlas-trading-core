from tests.a_share_owner_closeout_review_test_utils import AS_OF_DATE, make_paths, seed_closeout_outputs
from trading_core.equity_owner_closeout_review.closeout_review_audit import audit_a_share_owner_closeout_review


def test_closeout_review_audit_passes_and_fails_closed(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    passed = audit_a_share_owner_closeout_review(as_of_date=AS_OF_DATE, paths=paths)
    assert passed["overall_passed"] is True
    assert passed["closeout_checks"]["v090_rc_decision_consistent"] is True
    (paths.data_dir / "equity_owner_closeout_review" / "daily" / AS_OF_DATE / "closeout_manifest.json").unlink()
    failed = audit_a_share_owner_closeout_review(as_of_date=AS_OF_DATE, paths=paths)
    assert failed["overall_passed"] is False
    assert "json_artifacts_present" in failed["blocking_reasons"]
