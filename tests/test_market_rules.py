from trading_core.broker.market_rules import get_market_rule, is_t_plus_one, round_lot


def test_a_share_lot_and_t_plus_one() -> None:
    rule = get_market_rule("A_SHARE")
    assert rule.lot_size == 100
    assert round_lot(1250, "A_SHARE") == 1200
    assert is_t_plus_one("A_SHARE")
