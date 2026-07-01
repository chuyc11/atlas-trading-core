from trading_core.equity_owner_recovery_evidence.date_alignment import build_date_alignment


def test_recovery_evidence_date_alignment_blocks_mismatch():
    alignment = build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-25"}})
    assert alignment["overall_passed"] is False
    assert alignment["blocking_reasons"] == ["source_date_mismatch"]


def test_recovery_evidence_date_alignment_allows_mismatch():
    alignment = build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-25"}}, allow_date_mismatch=True)
    assert alignment["overall_passed"] is True
    assert alignment["warnings"] == ["source_date_mismatch_allowed"]

