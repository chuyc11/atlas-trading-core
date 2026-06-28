# A-Share Briefing Schema

This document describes `daily_stock_selection_briefing.json` for v0.7.7.

## Required Top-Level Fields

```json
{
  "briefing_id": "A-SHARE-DAILY-STOCK-SELECTION-BRIEFING",
  "target_version": "v0.7.7-a-share-daily-stock-selection-briefing",
  "as_of_date": "2026-06-26",
  "generated_at": "",
  "input_versions": {},
  "executive_summary": [],
  "long_candidates_top10": [],
  "mid_candidates_top10": [],
  "short_candidates_top10": [],
  "multi_horizon_candidates_top10": [],
  "risk_downgraded_summary": {},
  "virtual_portfolios": {
    "long": {},
    "mid": {},
    "short": {}
  },
  "industry_exposure_summary": {},
  "risk_liquidity_summary": {},
  "audit_status": {},
  "do_not_misread": [],
  "next_tracking_actions": [],
  "boundary": {}
}
```

## Candidate Records

Long, mid, and short candidate records contain rank, symbol, name, industry, horizon score, horizon rank, RiskScore, LiquidityScore, relevant component score, CompositeOpportunityScore, inclusion reasons, and risk reasons.

Multi-horizon records contain symbol, name, overlap type, best horizon, LongScore, MidScore, ShortScore, CompositeOpportunityScore, primary strengths, and risk notes.

Risk-downgraded records contain symbol, name, trigger horizon, trigger score, downgrade reason, RiskScore, LiquidityScore, and confidence.

## Virtual Portfolio Records

Each portfolio summary contains holding count, weight sum, max single weight, max industry weight, top 10 holdings by target weight, top industries, and risk notes.

Target weights are research tracking weights only. They are not real-account instructions.

## Boundary Fields

```json
{
  "briefing_only": true,
  "scores_regenerated": false,
  "candidates_regenerated": false,
  "virtual_portfolios_regenerated": false,
  "buy_sell_signals_generated": false,
  "order_preview_generated": false,
  "official_forward_dry_run_status_unchanged": true,
  "day2_executed": false,
  "run_daily_called": false,
  "broker_connected": false,
  "real_orders_placed": false,
  "model_profit_guaranteed": false,
  "live_trading_ready": false
}
```

Briefing schemas describe information summaries only. They are not trading advice, not score-generation contracts, not order contracts, and not broker contracts.

v0.7.8 tracking consumes the briefing manifest as an input source trace, but it does not change the v0.7.7 briefing schema. Paper ledger and holdings schemas are documented separately in `docs/A_SHARE_PAPER_LEDGER_SCHEMA.md` and `docs/A_SHARE_VIRTUAL_PORTFOLIO_TRACKING.md`.
