from trading_core.equity_build_output_ops_refresh.date_alignment import build_date_alignment


def test_build_output_ops_date_alignment_pass_fail_and_allow():
    availability = {"entries": [{"artifact_id": "x", "as_of_date": "2026-06-25"}]}
    failed = build_date_alignment(as_of_date="2026-06-26", input_availability=availability)
    assert failed["overall_passed"] is False
    allowed = build_date_alignment(as_of_date="2026-06-26", input_availability=availability, allow_date_mismatch=True)
    assert allowed["overall_passed"] is True

