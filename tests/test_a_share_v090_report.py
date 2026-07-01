from tests.a_share_v090_rc_test_utils import AS_OF_DATE, make_paths, seed_v090_outputs


def test_v090_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_v090_outputs(paths)
    out = paths.outputs_dir / "equity_owner_v090_rc" / "daily" / AS_OF_DATE
    assert (out / "A_SHARE_V090_RC_REPORT.md").exists()
    assert (out / "A_SHARE_V090_AUDIT_SWEEP_RESULT.md").exists()
    text = (out / "A_SHARE_V090_RC_REPORT.md").read_text(encoding="utf-8")
    assert "owner-readiness remains blocked" in text
