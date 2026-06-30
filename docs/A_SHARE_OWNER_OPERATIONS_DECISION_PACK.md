# A-Share Owner Operations Decision Pack

The v0.8.11 owner operations decision pack is generated at:

- `data/equity_owner_daily_pack/daily/YYYY-MM-DD/owner_operations_decision_pack.json`
- `outputs/equity_owner_daily_pack/daily/YYYY-MM-DD/A_SHARE_OWNER_DAILY_DECISION_PACK.md`

It summarizes:

- today status
- what changed today
- what the owner should review first
- research output digest
- candidate tracking digest
- virtual portfolio digest
- warning, issue, and safe-action digest
- protected path digest
- boundary digest
- artifact navigation
- next operational decision

Allowed operational decision categories:

- `no_action_required`
- `review_warnings`
- `review_safe_actions`
- `inspect_artifacts`
- `wait_for_more_history`
- `developer_follow_up`
- `rerun_audit_only`
- `hold_release`

Forbidden categories:

- `buy_stock`
- `sell_stock`
- `place_order`
- `rebalance_real_account`
- `connect_broker`
- `enable_live_trading`

This pack is not an investment decision pack. It is not a broker instruction, not an order instruction, not a buy/sell signal, not an order preview, not a real-account rebalance instruction, not a profit guarantee, and not live-trading readiness.

## v0.8.12 history usage

v0.8.12 reads this operations decision pack as one input to owner daily pack history and readiness trends. The trend layer records operational readiness only. It does not convert the operations decision into investment advice, a trade signal, a broker instruction, an order preview, or live readiness.
