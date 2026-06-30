from tests.a_share_owner_quality_exception_test_utils import AS_OF_DATE, make_paths, seed_owner_quality_exception_outputs


def test_quality_exception_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_quality_exception_outputs(paths)
    out = paths.outputs_dir / "equity_owner_quality_exceptions" / "daily" / AS_OF_DATE
    assert (out / "A_SHARE_OWNER_QUALITY_EXCEPTION_WORKFLOW.md").exists()
    assert (out / "A_SHARE_MANUAL_WAIVER_POLICY.md").exists()
    assert "不是投资建议" in (out / "A_SHARE_OWNER_QUALITY_EXCEPTION_WORKFLOW.md").read_text(encoding="utf-8")
