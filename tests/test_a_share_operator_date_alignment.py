from trading_core.equity_owner_operator_experience.date_alignment import build_date_alignment


def test_operator_date_alignment_pass_fail_and_allow():
    assert build_date_alignment(payloads={"a": {"as_of_date": "2026-06-26"}})["overall_passed"] is True
    failed = build_date_alignment(payloads={"a": {"as_of_date": "2026-06-25"}})
    assert failed["overall_passed"] is False
    allowed = build_date_alignment(payloads={"a": {"as_of_date": "2026-06-25"}}, allow_date_mismatch=True)
    assert allowed["overall_passed"] is True
