from tests.a_share_build_output_dashboard_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_build_output_dashboard.artifact_navigation import build_artifact_navigation


def test_build_output_artifact_navigation_generated(tmp_path):
    paths = make_paths(tmp_path)
    nav = build_artifact_navigation(paths=paths, as_of_date=AS_OF_DATE)
    assert nav["artifact_count"] > 0

