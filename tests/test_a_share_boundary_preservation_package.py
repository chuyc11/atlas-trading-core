from trading_core.equity_owner_evidence_backed_reevaluation_prep.preservation_packages import build_boundary_preservation_package


def test_boundary_preservation_package_blocks_trading_actions():
    package = build_boundary_preservation_package()
    assert package["research_only"] is True
    assert package["broker_connected"] is False
    assert package["real_orders_placed"] is False
    assert package["buy_sell_signals_generated"] is False

