from tests.a_share_operator_experience_test_utils import AS_OF_DATE, make_paths, seed_operator_outputs


def test_operator_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_operator_outputs(paths)
    out = paths.outputs_dir / "equity_owner_operator_experience" / "daily" / AS_OF_DATE
    assert (out / "A_SHARE_OWNER_DAILY_OPERATOR_STATUS.md").exists()
    assert (out / "A_SHARE_OPERATOR_QUICKSTART.md").exists()
    assert "不是投资建议" in (out / "A_SHARE_OWNER_DAILY_OPERATOR_STATUS.md").read_text(encoding="utf-8")
