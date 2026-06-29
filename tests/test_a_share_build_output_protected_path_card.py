from trading_core.equity_build_output_dashboard.protected_path_card import build_protected_path_card


def test_build_output_protected_path_card_distinguishes_preexisting():
    card = build_protected_path_card(as_of_date="2026-06-26", protected_check={"preexisting_protected_paths": ["data/orders"], "protected_path_modifications_detected": False})
    assert card["preexisting_protected_paths"] == ["data/orders"]
    assert card["protected_path_modifications_detected"] is False

