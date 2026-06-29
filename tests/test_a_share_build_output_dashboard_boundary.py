from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_output_dashboard.build_output_boundary import build_boundary_check


def test_build_output_boundary_clean(tmp_path):
    paths = make_paths(tmp_path)
    result = build_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warning_card={"blocking_reasons": [], "warnings": []}, source_resolution={"blocking_reasons": [], "warnings": []})
    assert result["overall_passed"] is True
    assert result["dashboard_used_as_trade_instruction"] is False

