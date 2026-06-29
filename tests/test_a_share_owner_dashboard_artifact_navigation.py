from tests.a_share_owner_dashboard_test_utils import AS_OF_DATE, make_paths, seed_owner_dashboard_inputs
from trading_core.equity_owner_dashboard.artifact_navigation import build_artifact_navigation_index


def test_artifact_navigation_lists_owner_priority_items(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_dashboard_inputs(paths)
    nav = build_artifact_navigation_index(paths=paths, as_of_date=AS_OF_DATE)
    assert nav["artifact_count"] >= 10
    assert any(row["owner_priority"] == "high" for row in nav["artifacts"])
