from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, write_text
from trading_core.equity_owner_dashboard.dashboard_boundary import build_dashboard_boundary_check


def test_boundary_fails_on_forbidden_artifact(tmp_path):
    paths = make_paths(tmp_path)
    write_text(paths.outputs_dir / "equity_owner_dashboard" / "daily" / AS_OF_DATE / "ORDER_PREVIEW.md")
    boundary = build_dashboard_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is False
    assert boundary["forbidden_artifacts_present"]
