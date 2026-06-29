from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_output_dashboard.dashboard_comparison import build_dashboard_comparison


def test_validate_dashboard_vs_build_dashboard_comparison_generated(tmp_path):
    paths = make_paths(tmp_path)
    result = build_dashboard_comparison(paths=paths, as_of_date=AS_OF_DATE, build_cards={"build_output_warning_and_blocker_card": {"overall_passed": True, "blocking_count": 0}}, source_resolution={"required_validate_fallback_used": False, "optional_validate_fallback_used": False})
    assert result["comparison_completed"] is True

