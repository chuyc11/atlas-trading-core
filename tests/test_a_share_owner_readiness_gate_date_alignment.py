from trading_core.equity_owner_readiness_gate.date_alignment import build_date_alignment


def test_owner_readiness_gate_date_alignment_passes():
    result = build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-26"}})
    assert result["overall_passed"] is True


def test_owner_readiness_gate_date_alignment_fails_unless_allowed():
    result = build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-25"}})
    assert result["overall_passed"] is False
    allowed = build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-25"}}, allow_date_mismatch=True)
    assert allowed["overall_passed"] is True
