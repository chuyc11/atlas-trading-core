from tests.a_share_owner_dashboard_test_utils import make_paths
from trading_core.equity_ops_center.artifact_navigation import build_ops_artifact_navigation


def test_ops_artifact_navigation_generated(tmp_path):
    paths = make_paths(tmp_path)
    path = paths.project_root / "data" / "x.json"
    path.write_text("{}", encoding="utf-8")
    nav = build_ops_artifact_navigation(paths=paths, as_of_date="2026-06-26", input_paths={"data_refresh_audit": path}, output_paths={})
    assert nav["entries"][0]["exists"] is True
    assert nav["entries"][0]["module_id"] == "data_refresh"
