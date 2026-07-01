from tests.a_share_recovery_evidence_test_utils import AS_OF_DATE, make_paths, seed_recovery_evidence_outputs


def test_recovery_evidence_reports_generated(tmp_path):
    paths = make_paths(tmp_path)
    seed_recovery_evidence_outputs(paths)
    root = paths.outputs_dir / "equity_owner_recovery_evidence" / "daily" / AS_OF_DATE
    assert (root / "A_SHARE_RECOVERY_EVIDENCE_COLLECTION.md").exists()
    assert (root / "A_SHARE_READINESS_IMPROVEMENT_EVIDENCE.md").exists()
    assert "不是正式 gate score" in (root / "A_SHARE_READINESS_IMPROVEMENT_EVIDENCE.md").read_text(encoding="utf-8")

