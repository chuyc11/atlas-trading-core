from tests.a_share_current_day_test_utils import AS_OF_DATE, make_paths
from trading_core.equity_current_day.current_day_boundary import build_current_day_boundary_check


def test_current_day_boundary_clean_by_default(tmp_path):
    paths = make_paths(tmp_path)
    boundary = build_current_day_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is True
    assert boundary["broker_connected"] is False
    assert boundary["real_orders_placed"] is False


def test_current_day_boundary_detects_forbidden_artifact(tmp_path):
    paths = make_paths(tmp_path)
    forbidden = paths.data_dir / "equity_current_day_runs" / "daily" / AS_OF_DATE / "ORDER_PREVIEW.md"
    forbidden.parent.mkdir(parents=True)
    forbidden.write_text("preview", encoding="utf-8")
    boundary = build_current_day_boundary_check(paths=paths, as_of_date=AS_OF_DATE, warnings=[], blocking_reasons=[])
    assert boundary["overall_passed"] is False
    assert "forbidden_artifacts_present" in boundary["blocking_reasons"]

