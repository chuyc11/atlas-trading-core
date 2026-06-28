# A Share Full Market AI Stock Selection Plan

## Positioning

The project upgrades from an ETF virtual trading MVP into an A-share full-market AI multi-horizon stock selection and virtual portfolio tracking system.

Priorities: stock selection quality, usability, daily executability, explainability, virtual portfolio tracking, and future adapter extensibility.

## Product Lines

- A-share full-market selection is the main line.
- ETF forward dry-run remains execution-rule foundation, virtual ledger foundation, benchmark, and control group.
- Tonghuashun, miniQMT, and broker adapters are future research only.

## v0.7 Roadmap

- v0.7.0 external project intake and A-share selection plan
- v0.7.1 A-share full-market data ingestion
  - implemented data-only foundation outputs: `data/equity_universe/equity_master.parquet`, `data/equity_universe/trading_calendar.parquet`, `data/equity_market/daily_price_panel.parquet`, `data/equity_market/adjusted_price_panel.parquet`, `data/equity_market/daily_basic_panel.parquet`, `data/equity_industry/industry_classification.parquet`, `data/equity_fundamental/basic_financials_panel.parquet`, `data/equity_data_quality/a_share_data_source_manifest.json`, `data/equity_data_quality/a_share_data_coverage_audit.json`, `data/equity_data_quality/a_share_data_schema_audit.json`
  - source priority: qstock-style public adapters, AkShare, Tushare if token exists, BaoStock, local CSV/Parquet, future Tonghuashun iFinD/QuantAPI
  - constraints: no LongScore/MidScore/ShortScore, no candidates, no virtual portfolios, no broker, no real orders, no `run-daily`, no official forward dry-run day2
  - current public-source limitation: the qstock-style public HTTP snapshot may be partial or delayed; coverage and schema audits are the release gate
- v0.7.1.1 A-share historical panel backfill
  - outputs: historical daily price, adjusted price, daily basic, financial panels, historical panel coverage audit, and feature readiness audit
  - constraints: no scores, no candidates, no watchlists, no virtual portfolios, no broker, no real orders, no `run-daily`, no official forward dry-run day2
  - purpose: prepare enough 20d/60d/120d/250d and financial history for v0.7.2 and v0.7.3
- v0.7.1.2 A-share historical data provider expansion
  - outputs: root-cause diagnostic, full-market symbol queue, checkpoint, batch manifests, per-symbol manifest, expanded historical panels, global coverage ratios, and passing readiness audits
  - constraints: still no scores, no candidates, no watchlists, no virtual portfolios, no broker, no real orders, no `run-daily`, no official forward dry-run day2
  - purpose: resolve the v0.7.1.1 10-symbol coverage blocker and authorize the data foundation to proceed to v0.7.2
- v0.7.2 tradable universe filter
  - filters: eligibility, ST/risk warning, listing age below 120 trading days, missing/suspended price, 20d/60d effective trading observations, 20d/60d average amount, total/circulating market cap, close price, price sanity, one-word limit up/down risk, and 20d/60d/120d/250d data coverage
  - outputs: `strict_tradable_universe`, `caution_universe`, `excluded_universe`, `unknown_status_universe`, reason breakdown, manifest, and audit
  - result as of 2026-06-26: 3676 strict tradable, 0 caution, 2191 excluded, 0 unknown
  - constraints: no LongScore/MidScore/ShortScore, no RiskScore/LiquidityScore, no candidates, no watchlists, no virtual portfolios, no broker, no real orders, no `run-daily`, no official forward dry-run day2
  - default downstream input: `strict_tradable_universe`; `caution_universe` is observation-only unless a future command explicitly allows it
- v0.7.3 multi-horizon feature engineering
  - long features: quality, ROE, gross margin, net margin, cash flow, leverage, valuation percentile, dividend, long-term trend
  - mid features: 60/120-day trend, relative strength, industry rotation, earnings improvement, volume confirmation, volatility-adjusted return
  - short features: 5/10/20-day momentum, breakout, pullback repair, volume-price confirmation, capital flow, short-term heat
  - risk/liquidity/industry features are separate first-class feature groups
- v0.7.4 Long/Mid/Short scoring system
  - implemented scoring-only outputs: LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, IndustryScore, FundamentalScore, CompositeOpportunityScore, ranks, percentiles, component breakdowns, distribution report, manifest, summary, and audit
  - result as of 2026-06-26: 3676 strict tradable symbols scored, scoring audit passed, recommended next version `v0.7.5-a-share-candidate-generation-system`
  - constraints: no candidates, no watchlists, no virtual portfolios, no buy/sell signals, no broker, no real orders, no `run-daily`, no profit guarantee, no live-trading readiness, no official forward dry-run day2
- v0.7.5 candidate generation
  - implemented candidate-generation outputs: long candidates, mid candidates, short candidates, extended watch pool, multi-horizon candidates, risk-downgraded candidates, reason breakdown, manifest, summary, reports, and audit
  - result as of 2026-06-26: 30 long candidates, 30 mid candidates, 30 short candidates, 300 extended watch-pool records, 50 multi-horizon candidates, 294 risk-downgraded candidates, candidate audit passed, recommended next version `v0.7.6-a-share-virtual-portfolio-construction`
  - constraints: candidates are research inputs only, not investment advice, not buy/sell signals, not order instructions, not virtual portfolios, not broker access, not real orders, not `run-daily`, not profit guarantee, not live-trading readiness, no official forward dry-run day2
- v0.7.6 three virtual portfolios
  - implemented virtual-only outputs: long virtual portfolio, mid virtual portfolio, short virtual portfolio, target weights, industry exposure, risk/liquidity summary, manifest, reports, and audit
  - result as of 2026-06-26: 30 long holdings, 30 mid holdings, 20 short holdings, all weight sums 1.0, virtual portfolio audit passed, recommended next version `v0.7.7-a-share-daily-stock-selection-briefing`
  - constraints: virtual portfolios are not real portfolios, virtual target weights are not order instructions, no buy/sell signals, no broker order preview, no broker, no real orders, no `run-daily`, no profit guarantee, no live-trading readiness, no official forward dry-run day2
- v0.7.7 daily AI stock selection briefing
  - implemented briefing-only outputs: daily stock selection briefing JSON, Markdown briefing, source trace, manifest, boundary check, and audit
  - result as of 2026-06-26: all required sections present, source trace complete, briefing audit passed, recommended next version `v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger`
  - constraints: reads existing artifacts only, no score regeneration, no candidate regeneration, no virtual portfolio regeneration, no buy/sell signals, no order previews, no broker, no real orders, no `run-daily`, no profit guarantee, no live-trading readiness
- v0.7.8 virtual portfolio tracking and paper ledger
  - implemented virtual-only outputs: tracking config, long/mid/short paper ledgers, holdings snapshots, NAV, performance, drawdown, exposure, benchmark comparison, manifest, source trace, reports, and audit
  - result as of 2026-06-26: 30 long holdings, 30 mid holdings, 20 short holdings, all NAVs 1000000.0, all weight sums approximately 1.0, tracking audit passed, recommended next version `v0.7.9-a-share-daily-workflow-orchestration`
  - constraints: paper ledger is not a real-money ledger, virtual holdings are not real holdings, virtual returns are not actual returns, no buy/sell signals, no order previews, no broker, no real orders, no `run-daily`, no profit guarantee, no live-trading readiness
- v0.7.9 daily workflow orchestration
  - output: daily workflow orchestration around data refresh, briefing, virtual tracking, audits, and owner-facing reports
- v0.8.0 Tonghuashun, miniQMT, and simulated adapter research
  - adapter research only: read-only quote/account sync, simulated adapter experiments, order preview, manual confirmation gate
- v0.9.0 manual-confirmation trading preparation
  - required gates: manual confirmation, kill switch, max position, max daily turnover, max drawdown stop, order preview diff, pre-trade risk check, post-trade reconciliation

## Proposed Directories

- `external_research/`
- `src/trading_core/external_intake/`
- `src/trading_core/equity_universe/`
- `src/trading_core/equity_data/`
- `src/trading_core/equity_industry/`
- `src/trading_core/equity_fundamental/`
- `src/trading_core/equity_data_quality/`
- `src/trading_core/equity_selection/`
- `src/trading_core/equity_features/`
- `src/trading_core/equity_scoring/`
- `src/trading_core/equity_portfolios/`
- `src/trading_core/equity_briefings/`
- `src/trading_core/equity_portfolio_tracking/`
- `src/trading_core/equity_validation/`
- `src/trading_core/integrations/`
- `data/equity_universe/`, `data/equity_market/`, `data/equity_industry/`, `data/equity_fundamental/`, `data/equity_data_quality/`, `data/equity_features/`, `data/equity_scores/`, `data/equity_selection/`, `data/equity_portfolios/`, `data/equity_briefings/`, `data/equity_portfolio_tracking/`, `data/equity_validation/`
- `outputs/equity_selection/`, `outputs/equity_scores/`, `outputs/equity_portfolios/`, `outputs/equity_briefings/`, `outputs/equity_portfolio_tracking/`, `outputs/equity_validation/`

## Required Boundary

- No real trading.
- No broker connection.
- No real orders.
- No third-party trading code merged into the main flow.
- No LLM direct trading decision.
- No model profit guarantee.
- ETF forward dry-run status unchanged.
- `run-daily` not called.
- Data ingestion artifacts are not stock recommendations.
- Free public data source gaps must be recorded in source manifests and audits.
- v0.7.4 scores are relative research inputs only; they are not recommendations, candidates, watchlists, portfolio actions, buy/sell signals, or profit claims.
- v0.7.5 candidates are research inputs only; they are not investment advice, buy/sell signals, portfolio actions, order instructions, broker instructions, real orders, or profit claims.
- v0.7.6 virtual portfolios are research-only virtual tracking inputs; they are not real portfolios, buy/sell signals, order previews, broker instructions, real orders, or profit claims.
- v0.7.7 daily briefing is an information summary only; it does not regenerate scores, candidates, virtual portfolios, buy/sell signals, order previews, broker artifacts, real orders, or profit claims.
- v0.7.8 virtual tracking and paper ledger artifacts are research-only; paper ledgers are not real-money ledgers, virtual holdings are not real holdings, virtual returns are not actual returns, and no broker/order/live-trading claim is generated.
