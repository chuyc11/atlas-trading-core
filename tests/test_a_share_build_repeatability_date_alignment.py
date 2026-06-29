from trading_core.equity_build_repeatability.date_alignment import build_repeatability_date_alignment


def test_repeatability_date_alignment_passes_without_mismatch():
    result = build_repeatability_date_alignment(as_of_date="2026-06-26", input_availability={"entries": []})
    assert result["overall_passed"] is True


def test_repeatability_date_alignment_fails_closed():
    result = build_repeatability_date_alignment(
        as_of_date="2026-06-26",
        input_availability={"entries": [{"artifact_id": "x", "as_of_date": "2026-06-25"}]},
    )
    assert result["overall_passed"] is False

