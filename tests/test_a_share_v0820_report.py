from tests.a_share_v0820_test_utils import AS_OF_DATE, make_paths, seed_v0820_outputs


def test_v0820_reports_generated_without_forbidden_wording(tmp_path):
    paths = make_paths(tmp_path)
    seed_v0820_outputs(paths)
    report = paths.outputs_dir / "equity_owner_v0820_gate_outcome" / "daily" / AS_OF_DATE / "A_SHARE_V0820_OWNER_GATE_OUTCOME.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "final_blocked_closeout" in text
    assert "买入建议" not in text

