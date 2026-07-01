from tests.a_share_v09_platform_test_utils import AS_OF_DATE, platform_json, seed_v09_inputs
from trading_core.equity_v09_platform import run_a_share_v09_daily_platform


def test_v09_simulated_account_virtual_broker_and_ledger_are_simulation_only(tmp_path):
    paths = seed_v09_inputs(tmp_path)
    run_a_share_v09_daily_platform(paths=paths, as_of_date=AS_OF_DATE, simulation_only=True)
    account = platform_json(paths, "v09_simulated_account_state")
    execution = platform_json(paths, "v09_virtual_broker_execution_report")
    ledger = platform_json(paths, "v09_paper_ledger_snapshot")

    assert account["simulated_nav"] > 0
    assert execution["simulated_order_intent_count"] == 2
    assert execution["real_orders_placed"] is False
    assert execution["real_order_preview_generated"] is False
    assert execution["buy_sell_signals_generated"] is False
    assert all(fill["not_real_fill"] for fill in execution["simulated_fills"])
    assert ledger["ledger_consistency_passed"] is True
    assert ledger["not_real_ledger"] is True
