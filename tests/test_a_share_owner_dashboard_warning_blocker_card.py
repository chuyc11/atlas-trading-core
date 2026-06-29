from trading_core.equity_owner_dashboard.warning_blocker_card import build_warning_and_blocker_card


def test_warning_blocker_card_classifies_known_non_blocking_warning():
    card = build_warning_and_blocker_card(as_of_date="2026-06-26", sources={"refresh": {"warnings": ["daily_basic:required_field_all_null"], "blocking_reasons": []}})
    assert card["overall_passed"] is True
    assert card["items"][0]["known_non_blocking"] is True
