# A-Share Paper Ledger Schema

The v0.7.8 paper ledger is a research-only virtual ledger. It is not a real account ledger and is not an execution ledger.

## Ledger Files

- `data/equity_portfolio_tracking/daily/YYYY-MM-DD/long_paper_ledger.json`
- `data/equity_portfolio_tracking/daily/YYYY-MM-DD/mid_paper_ledger.json`
- `data/equity_portfolio_tracking/daily/YYYY-MM-DD/short_paper_ledger.json`

## Record Fields

Each record contains:

- `ledger_id`
- `as_of_date`
- `ledger_start_date`
- `portfolio_id`
- `portfolio_horizon`
- `record_type`
- `symbol`
- `name`
- `virtual_position_value`
- `virtual_shares`
- `entry_price`
- `mark_price`
- `target_weight`
- `actual_weight`
- `cash_effect`
- `virtual_cash_balance_after`
- `unrealized_pnl`
- `unrealized_return`
- `source_virtual_portfolio_path`
- `created_at`

## Allowed Record Types

- `virtual_initial_position`
- `virtual_mark_to_market`
- `virtual_cash_balance`

The initial v0.7.8 build uses `virtual_initial_position`.

## Forbidden Record Types

- `buy_order`
- `sell_order`
- `real_trade`
- `broker_fill`
- `order_preview`

## Boundary Flags

Each record must include:

- `virtual_only=true`
- `research_only=true`
- `not_real_trade=true`
- `not_buy_signal=true`
- `not_sell_signal=true`
- `not_order_instruction=true`
- `not_profit_guarantee=true`
- `not_live_trading_ready=true`

Fractional shares are allowed because this is research tracking, not board-lot execution simulation.
