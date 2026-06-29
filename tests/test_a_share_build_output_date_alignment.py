from trading_core.equity_build_output_dashboard.date_alignment import build_date_alignment


def test_build_output_date_alignment_passes():
    assert build_date_alignment(as_of_date="2026-06-26", input_availability={"entries": []})["overall_passed"]


def test_build_output_date_alignment_fails():
    result = build_date_alignment(as_of_date="2026-06-26", input_availability={"entries": [{"artifact_id": "x", "as_of_date": "2026-06-25"}]})
    assert result["overall_passed"] is False

