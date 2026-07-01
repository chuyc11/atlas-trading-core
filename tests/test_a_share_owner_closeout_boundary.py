from tests.a_share_owner_closeout_review_test_utils import AS_OF_DATE, make_paths, seed_closeout_outputs, closeout_data
from trading_core.equity_owner_closeout_review.boundary import build_boundary_check


def test_closeout_boundary_clean_and_forbidden_wording_blocked(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    boundary = closeout_data(paths, "closeout_boundary_check.json")
    assert boundary["overall_passed"] is True
    assert boundary["old_run_daily_called"] is False
    assert boundary["closeout_review_used_as_trade_instruction"] is False
    bad_report = paths.outputs_dir / "equity_owner_closeout_review" / "daily" / AS_OF_DATE / "BAD.md"
    bad_report.write_text("买入建议", encoding="utf-8")
    failed = build_boundary_check(paths=paths, as_of_date=AS_OF_DATE)
    assert failed["overall_passed"] is False
    assert "forbidden_positive_wording_present" in failed["blocking_reasons"]
