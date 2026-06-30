from tests.a_share_controlled_gate_reevaluation_test_utils import AS_OF_DATE, make_paths, seed_controlled_gate_reevaluation_outputs


def test_controlled_gate_reevaluation_reports_written(tmp_path):
    paths = make_paths(tmp_path)
    seed_controlled_gate_reevaluation_outputs(paths)
    root = paths.outputs_dir / "equity_owner_controlled_gate_reevaluation" / "daily" / AS_OF_DATE
    assert (root / "A_SHARE_CONTROLLED_GATE_REEVALUATION.md").exists()
    assert (root / "A_SHARE_REEVALUATION_SKIPPED_NOT_READY.md").exists()
    assert "skipped_not_ready" in (root / "A_SHARE_CONTROLLED_GATE_REEVALUATION.md").read_text(encoding="utf-8")

