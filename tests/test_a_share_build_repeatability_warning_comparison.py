from tests.a_share_build_repeatability_test_utils import AS_OF_DATE, make_paths, write_json
from trading_core.equity_build_repeatability.warning_comparison import build_repeatability_warning_comparison


def test_repeatability_warning_comparison_generates_new_warning_list(tmp_path):
    paths = make_paths(tmp_path)
    write_json(paths.data_dir / "equity_current_day_builds" / "daily" / AS_OF_DATE / "gated_build_summary.json", {"warnings": ["a"]})
    result = build_repeatability_warning_comparison(paths=paths, as_of_date=AS_OF_DATE, execution_record={"warnings": ["a", "b"]})
    assert result["new_warnings"] == ["b"]

