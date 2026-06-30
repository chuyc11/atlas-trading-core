from trading_core.equity_owner_daily_pack_history.date_alignment import build_date_alignment


def test_owner_daily_pack_history_date_alignment_passes():
    result = build_date_alignment(as_of_date="2026-06-26", input_availability={"entries": [{"artifact_id": "x", "as_of_date": "2026-06-26"}]})
    assert result["overall_passed"] is True


def test_owner_daily_pack_history_date_alignment_fails_unless_allowed():
    availability = {"entries": [{"artifact_id": "x", "as_of_date": "2026-06-25"}]}
    blocked = build_date_alignment(as_of_date="2026-06-26", input_availability=availability)
    allowed = build_date_alignment(as_of_date="2026-06-26", input_availability=availability, allow_date_mismatch=True)
    assert blocked["overall_passed"] is False
    assert allowed["overall_passed"] is True
