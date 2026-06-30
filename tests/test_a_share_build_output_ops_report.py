from tests.a_share_build_output_ops_test_utils import AS_OF_DATE, make_paths, seed_build_output_ops_outputs


def test_build_output_ops_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_build_output_ops_outputs(paths)
    out = paths.outputs_dir / "equity_build_output_ops_refresh" / "daily" / AS_OF_DATE
    report = (out / "A_SHARE_BUILD_OUTPUT_OPS_REFRESH.md").read_text(encoding="utf-8")
    assert "Build Output Ops Refresh 总览" in report
    assert "安全边界" in report
    assert "not a trade instruction" in report
    assert (out / "A_SHARE_BUILD_OUTPUT_MONITORING_REFRESH.md").exists()
    assert (out / "A_SHARE_BUILD_OUTPUT_REMEDIATION_REFRESH.md").exists()
    assert (out / "A_SHARE_BUILD_OUTPUT_OPS_CENTER_REFRESH.md").exists()

