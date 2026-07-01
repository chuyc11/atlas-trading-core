from trading_core.equity_owner_v090_rc.date_alignment import build_date_alignment


def test_v090_date_alignment_passes_and_fails_on_mismatch():
    passed = build_date_alignment(as_of_date="2026-06-26", payloads={"source": {"as_of_date": "2026-06-26"}})
    assert passed["overall_passed"] is True
    failed = build_date_alignment(as_of_date="2026-06-26", payloads={"source": {"as_of_date": "2026-06-25"}})
    assert failed["overall_passed"] is False
    allowed = build_date_alignment(as_of_date="2026-06-26", payloads={"source": {"as_of_date": "2026-06-25"}}, allow_date_mismatch=True)
    assert allowed["overall_passed"] is True
