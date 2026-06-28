# A-Share Briefing Audit

`audit-a-share-daily-stock-selection-briefing` validates v0.7.7 briefing artifacts.

## Audit Scope

The audit checks:

- briefing JSON exists
- briefing Markdown exists
- briefing manifest exists
- source trace JSON and Markdown exist
- boundary check exists
- all required sections are present
- long/mid/short candidate Top 10 sections exist
- multi-horizon, risk-downgraded, virtual portfolio, industry exposure, risk/liquidity, audit status, do-not-misread, and next tracking sections exist
- source trace covers every required section
- source trace paths point to existing non-briefing upstream artifacts
- scores_regenerated=false
- candidates_regenerated=false
- virtual_portfolios_regenerated=false
- buy_sell_signals_generated=false
- order_preview_generated=false
- broker_connected=false
- real_orders_placed=false
- model_profit_guaranteed=false
- live_trading_ready=false
- forbidden positive wording is absent

## Audit Outputs

- `data/equity_data_quality/a_share_daily_stock_selection_briefing_audit.json`
- `outputs/audit/A_SHARE_DAILY_STOCK_SELECTION_BRIEFING_AUDIT.md`

Passing audit recommends:

```text
v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger
```

v0.7.8 implements that recommended virtual tracking handoff. Its own audit recommends `v0.7.9-a-share-daily-workflow-orchestration` only after tracking artifacts pass.

Failing audit recommends:

```text
v0.7.7.1-a-share-daily-stock-selection-briefing-remediation
```

## Boundary

The audit is a release gate for briefing quality. It is not a trading authorization gate. Passing audit does not approve real trading, buy/sell signals, order previews, broker connection, real orders, profit claims, or live-trading readiness.
