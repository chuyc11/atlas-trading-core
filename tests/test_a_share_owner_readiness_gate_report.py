from tests.a_share_owner_readiness_gate_test_utils import AS_OF_DATE, make_paths, seed_owner_readiness_gate_outputs


def test_owner_readiness_gate_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_owner_readiness_gate_outputs(paths)
    out = paths.outputs_dir / "equity_owner_readiness_gate" / "daily" / AS_OF_DATE
    assert (out / "A_SHARE_OWNER_READINESS_GATE.md").exists()
    assert (out / "A_SHARE_DAILY_PACK_QUALITY_THRESHOLDS.md").exists()
    assert "不是投资建议" in (out / "A_SHARE_OWNER_RELEASE_RECOMMENDATION.md").read_text(encoding="utf-8")
