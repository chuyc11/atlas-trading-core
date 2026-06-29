from trading_core.equity_build_output_dashboard.warning_blocker_card import build_warning_and_blocker_card


def test_warning_blocker_card_treats_timestamp_hash_drift_as_warning():
    card = build_warning_and_blocker_card(
        as_of_date="2026-06-26",
        cards={"build_output_repeatability_card": {"timestamp_only_drift_count": 1, "metadata_hash_drift_count": 1, "business_output_drift_count": 0}, "build_output_protected_path_card": {"protected_path_modifications_detected": False}},
        availability={"warnings": [], "blocking_reasons": []},
        resolution={"warnings": [], "blocking_reasons": []},
    )
    assert card["overall_passed"] is True
    assert card["warning_count"] == 2

