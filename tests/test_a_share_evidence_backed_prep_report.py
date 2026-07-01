from tests.a_share_evidence_backed_prep_test_utils import AS_OF_DATE, make_paths, seed_evidence_backed_prep_outputs


def test_evidence_backed_prep_reports_generated_without_forbidden_wording(tmp_path):
    paths = make_paths(tmp_path)
    seed_evidence_backed_prep_outputs(paths)
    report_dir = paths.outputs_dir / "equity_owner_evidence_backed_reevaluation_prep" / "daily" / AS_OF_DATE
    report = report_dir / "A_SHARE_EVIDENCE_BACKED_GATE_REEVALUATION_PREP.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "No new formal gate score" in text
    assert "买入建议" not in text

