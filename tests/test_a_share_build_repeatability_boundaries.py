from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, seed_repeatability_outputs
from trading_core.equity_build_repeatability.repeatability_audit import audit_a_share_build_repeatability


def test_repeatability_boundaries_stay_clean(tmp_path):
    paths = make_paths(tmp_path)
    seed_repeatability_outputs(paths)
    audit = audit_a_share_build_repeatability(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True
    assert audit["execution_checks"]["old_run_daily_called"] is False
    assert audit["protected_path_checks"]["protected_path_modifications_detected"] is False

