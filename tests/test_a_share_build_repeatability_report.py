from trading_core.equity_build_repeatability.repeatability_report import render_protected_path_report


def test_repeatability_report_mentions_preexisting_paths_are_not_modifications():
    text = render_protected_path_report(
        as_of_date="2026-06-26",
        protected_check={"preexisting_protected_paths_allowed": True, "protected_path_modifications_detected": False},
    )
    assert "预先存在不等于本次生成或修改" in text

