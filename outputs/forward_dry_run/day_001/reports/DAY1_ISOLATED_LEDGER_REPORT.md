# Day1 Isolated Ledger Report

- forward_dry_run_ledger_written: true
- ledger_path_root: data/forward_dry_run
- virtual_cash: {'currency': 'CNY', 'initial_cash': 3000000.0, 'cash': 99940.149172}
- virtual_positions_count: 8
- virtual_valuation: {'cash': 99940.149172, 'market_value': 2896293.842745, 'total_equity': 2996233.991917}
- fills_rejects_summary: {'fills': 16, 'rejects': 0}
- cost_summary: {'commission': 869.757028, 'tax': 0.0, 'slippage': 0.073202, 'gross': 2896293.842745, 'net': 2900059.850828}
- ledger_hash: 3865de0f605a329e3e0dacd3c3999b723d77397c1a8f8700b714b4f374e2c2e5
- invariants: {'cash_non_negative': True, 'positions_non_negative': True, 'available_shares_valid': True}
- main_orders_written: false
- main_trades_written: false
- main_portfolio_written: false
- main_accounts_written: false

## Boundary
- Report generation only.
- Day 2 was not executed.
- Day 3 was not executed.
- run-daily was not called.
- No external market API was called.
- No real-time market data was downloaded.
- Main orders, trades, portfolio, and accounts ledgers were not written.
- No broker is connected.
- No real orders were placed.
- ML, LLM, and RL were not used for trading authorization.
- No promotion was triggered.
- This is not strategy effectiveness proof.
- This is not full forward dry-run validation.
- This is not live trading readiness.
