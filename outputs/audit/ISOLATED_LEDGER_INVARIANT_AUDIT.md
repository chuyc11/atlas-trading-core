# Isolated Ledger Invariant Audit

## Overall Verdict
- overall_passed=true
- blocking_reasons=[]

## Invariants
- cash_non_negative: true
- positions_non_negative: true
- available_lte_position: true
- no_same_day_sell_of_t_day_buys: true
- trades_link_to_accepted_orders: true
- rejected_orders_have_reason: true
- fills_have_price_and_costs: true
- costs_reconcile_to_cash: true
- valuations_reconcile: true
- isolated_outputs_only: true
- protected_paths: true

## Boundary
- isolated ledger invariant audit only
- run-daily not called
- forward dry-run not started
- main ledger not written
