from tests.a_share_owner_closeout_review_test_utils import AS_OF_DATE, make_paths, seed_closeout_outputs


def test_closeout_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_closeout_outputs(paths)
    out = paths.outputs_dir / "equity_owner_closeout_review" / "daily" / AS_OF_DATE
    assert (out / "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md").exists()
    assert (out / "A_SHARE_V090_FULL_REGRESSION_PLAN.md").exists()
    text = (out / "A_SHARE_OWNER_READINESS_CLOSEOUT_REVIEW.md").read_text(encoding="utf-8")
    assert "full pytest 留到 v0.9.0 执行" in text
