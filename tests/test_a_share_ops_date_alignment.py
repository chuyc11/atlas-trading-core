from trading_core.equity_ops_center.date_alignment import build_ops_date_alignment


def test_ops_date_alignment_passes_and_fails():
    ok = build_ops_date_alignment(as_of_date="2026-06-26", payloads={"x_audit": {"as_of_date": "2026-06-26"}})
    bad = build_ops_date_alignment(as_of_date="2026-06-26", payloads={"x_audit": {"as_of_date": "2026-06-25"}})
    assert ok["all_dates_aligned"] is True
    assert bad["all_dates_aligned"] is False
    assert bad["blocking_reasons"]
