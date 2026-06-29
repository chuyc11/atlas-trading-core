from tests.a_share_gated_build_test_utils import seed_gated_build_outputs
from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day_builds.gated_build_audit import audit_a_share_gated_build


def test_gated_build_audit_passes_for_seeded_outputs(tmp_path):
    paths = make_paths(tmp_path)
    seed_gated_build_outputs(paths)
    audit = audit_a_share_gated_build(as_of_date=AS_OF_DATE, paths=paths)
    assert audit["overall_passed"] is True

