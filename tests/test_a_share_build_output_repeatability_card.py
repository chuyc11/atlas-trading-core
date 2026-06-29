from trading_core.equity_build_output_dashboard.repeatability_card import build_repeatability_card


def test_build_output_repeatability_card_generated():
    card = build_repeatability_card(as_of_date="2026-06-26", repeatability_audit={"overall_passed": True}, comparison={"business_output_drift_count": 0})
    assert card["repeatability_audit_passed"] is True
    assert card["business_output_drift_count"] == 0

