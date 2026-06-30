from trading_core.equity_owner_quality_exceptions.date_alignment import build_date_alignment


def test_quality_exception_date_alignment_pass_fail():
    assert build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-26"}})["overall_passed"] is True
    failed = build_date_alignment(as_of_date="2026-06-26", payloads={"x": {"as_of_date": "2026-06-25"}})
    assert failed["overall_passed"] is False
