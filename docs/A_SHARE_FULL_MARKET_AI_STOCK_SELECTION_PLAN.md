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
  - outputs: `data/equity_universe/equity_master.parquet`, `data/equity_universe/trading_calendar.parquet`, `data/equity_market/daily_price_panel.parquet`, `data/equity_market/adjusted_price_panel.parquet`, `data/equity_market/daily_basic_panel.parquet`, `data/equity_fundamental/financial_panel.parquet`, `data/system/a_share_data_coverage_audit.json`, `outputs/audit/A_SHARE_DATA_COVERAGE_AUDIT.md`
  - source priority: qstock-style public adapters, AkShare, Tushare if token exists, BaoStock, local CSV/Parquet, future Tonghuashun iFinD/QuantAPI
- v0.7.2 tradable universe filter
  - filters: ST/*ST, delisting board, suspended stocks, listing age below 120 trading days, less than 18 effective trading days in the last 20, 20-day average amount below 50 million CNY, market cap below 3 billion CNY, price below 2 CNY, severe missing fundamentals, one-word limit-up/down execution risk, unresolved abnormal volatility
  - outputs: `tradable_universe.json`, `excluded_universe.json`, and `TRADABLE_UNIVERSE_REPORT.md`
- v0.7.3 multi-horizon feature engineering
  - long features: quality, ROE, gross margin, net margin, cash flow, leverage, valuation percentile, dividend, long-term trend
  - mid features: 60/120-day trend, relative strength, industry rotation, earnings improvement, volume confirmation, volatility-adjusted return
  - short features: 5/10/20-day momentum, breakout, pullback repair, volume-price confirmation, capital flow, short-term heat
  - risk/liquidity/industry features are separate first-class feature groups
- v0.7.4 Long/Mid/Short scoring system
  - scores: LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, IndustryScore, CompositeOpportunityScore
  - candidate gates: long 75/45/60, mid 75/55/65, short 80/65/75 for score/risk/liquidity
- v0.7.5 candidate generation
  - daily outputs: long 30, mid 30, short 30, watchlist 100-150, top 10 per horizon in the briefing
- v0.7.6 three virtual portfolios
  - portfolios: long 20-40, mid 20-40, short 10-30; virtual only
- v0.7.7 daily AI stock selection briefing
  - output: `outputs/equity_selection/daily/YYYY-MM-DD/DAILY_STOCK_SELECTION_BRIEFING.md`
  - must state: research and virtual tracking only, not investment advice, no broker connection, no real orders, no profit guarantee
- v0.7.8 historical walk-forward validation
  - validates Top 10/Top 30 long/mid/short, composite pool, removal pool, and risk-alert pool on 5/10/20/60/120-day horizons
- v0.7.9 30-day virtual forward tracking
  - output: daily briefings plus `OWNER_30DAY_STOCK_SELECTION_BRIEFING.md`
- v0.8.0 Tonghuashun, miniQMT, and simulated adapter research
  - adapter research only: read-only quote/account sync, simulated adapter experiments, order preview, manual confirmation gate
- v0.9.0 manual-confirmation trading preparation
  - required gates: manual confirmation, kill switch, max position, max daily turnover, max drawdown stop, order preview diff, pre-trade risk check, post-trade reconciliation

## Proposed Directories

- `external_research/`
- `src/trading_core/external_intake/`
- `src/trading_core/equity_universe/`
- `src/trading_core/equity_data/`
- `src/trading_core/equity_features/`
- `src/trading_core/equity_scoring/`
- `src/trading_core/equity_selection/`
- `src/trading_core/equity_portfolios/`
- `src/trading_core/equity_briefing/`
- `src/trading_core/equity_validation/`
- `src/trading_core/integrations/`
- `data/equity_universe/`, `data/equity_market/`, `data/equity_fundamental/`, `data/equity_features/`, `data/equity_scores/`, `data/equity_selection/`, `data/equity_portfolios/`, `data/equity_validation/`
- `outputs/equity_selection/`, `outputs/equity_portfolios/`, `outputs/equity_validation/`

## Required Boundary

- No real trading.
- No broker connection.
- No real orders.
- No third-party trading code merged into the main flow.
- No LLM direct trading decision.
- No model profit guarantee.
- ETF forward dry-run status unchanged.
- `run-daily` not called.
