# v0.7 Architecture

Positioning: A-share full-market AI multi-horizon stock selection and virtual portfolio tracking system

## Data Flow
- Public/local provider adapters
- A-share universe and trading calendar
- daily price, adjusted price, daily basic, industry, and basic financial data panels
- historical price, adjusted price, daily basic, and financial panels
- coverage audit and schema audit
- historical coverage audit and feature readiness audit
- tradable universe filter with strict/caution/excluded/unknown buckets
- long/mid/short feature sets
- LongScore/MidScore/ShortScore/RiskScore/LiquidityScore/IndustryScore
- candidate pools and watchlists
- long/mid/short virtual portfolios
- daily Chinese owner briefing
- walk-forward validation

## Modules
- `src/trading_core/external_intake/`
- `src/trading_core/integrations/public_data/`
- `src/trading_core/equity_universe/`
- `src/trading_core/equity_data/`
- `src/trading_core/equity_industry/`
- `src/trading_core/equity_fundamental/`
- `src/trading_core/equity_data_quality/`
- `src/trading_core/equity_features/`
- `src/trading_core/equity_scoring/`
- `src/trading_core/equity_selection/`
- `src/trading_core/equity_portfolios/`
- `src/trading_core/equity_briefing/`
- `src/trading_core/equity_validation/`
- `src/trading_core/integrations/`

## Mermaid

```mermaid
flowchart TD
  P["Public / local A-share provider adapters"] --> U["Equity master and trading calendar"]
  U --> M["Daily price / adjusted price / daily basic panels"]
  U --> I["Industry and basic financial panels"]
  M --> Q["Coverage audit and schema audit"]
  I --> Q
  Q --> B["Tradable universe filter"]
  B --> C["Strict tradable universe"]
  C --> D0["Long / Mid / Short features"]
  D0 --> D["LongScore / MidScore / ShortScore"]
  D --> E["Candidates / watchlist / risk alerts"]
  E --> F["Long / Mid / Short virtual portfolios"]
  F --> G["Daily Chinese owner briefing"]
  G --> H["Walk-forward validation"]
  X["ETF forward dry-run"] --> J["Benchmark / control group"]
  K["Future adapters"] -. "research only" .-> F
```

## v0.7.1 Data Foundation

v0.7.1 implements the first data-only layer. It writes local artifacts for:

- A-share equity master and SSE/SZSE/BSE calendar.
- daily price, adjusted price, daily basic, industry, and basic financial panels.
- data source manifest, coverage audit, and schema audit.

The current public provider path is a qstock-style public HTTP adapter. It does not import third-party project code. When a public endpoint is delayed, partial, or unavailable, the provider result must be recorded in the manifest and the coverage audit must fail closed if the key master/calendar/daily-price foundation is insufficient.

v0.7.1 does not generate recommendations, scores, candidates, virtual portfolios, or trade instructions. Later filters, features, scores, and portfolios must consume the audited local data artifacts rather than calling provider APIs directly.

## v0.7.1.1 Historical Panel Backfill

v0.7.1.1 fills historical panels required by later filters and features. It remains data-only and readiness-audit-only. If minimum historical coverage is not met, the workflow must fail closed and no success release tag should be created.

## v0.7.1.2 Historical Data Provider Expansion

v0.7.1.2 resolves the v0.7.1.1 coverage blocker by diagnosing the 10-symbol sample result, building a full-market A-share queue from `equity_master.parquet`, adding provider fallback adapters, checkpoint/resume, batch manifests, per-symbol manifests, and global coverage ratios. It prepares the audited local data foundation for v0.7.2 tradable-universe filtering.

It still does not generate scores, candidates, watchlists, virtual portfolios, orders, broker connections, `run-daily` output, or official forward dry-run day2 artifacts.

## v0.7.2 Tradable Universe Filter

v0.7.2 consumes the audited local A-share master, trading calendar, historical price panels, daily basic data, industry classification, financial history, symbol manifest, and readiness audits. It writes daily filter artifacts under `data/equity_selection/daily/YYYY-MM-DD/` and reports under `outputs/equity_selection/daily/YYYY-MM-DD/`.

The output buckets are `strict_tradable_universe`, `caution_universe`, `excluded_universe`, and `unknown_status_universe`. Future v0.7.3 feature engineering defaults to `strict_tradable_universe`; caution names are observation-only unless a future command explicitly allows them.

v0.7.2 does not generate scores, candidates, watchlists, virtual portfolios, orders, broker connections, `run-daily` output, or official forward dry-run day2 artifacts.

## v0.7.3 Multi-Horizon Feature Engineering

v0.7.3 consumes the `strict_tradable_universe` output from v0.7.2 and audited historical panels from v0.7.1.2. It writes feature tables under `data/equity_features/daily/YYYY-MM-DD/`, reports under `outputs/equity_features/daily/YYYY-MM-DD/`, and a release audit under `data/equity_data_quality/` and `outputs/audit/`.

The feature groups are short horizon, mid horizon, long horizon, risk, liquidity, industry, and fundamental. These are atomic inputs for a future scoring stage. The stage does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, orders, broker connections, `run-daily` output, profit claims, live readiness, or official forward dry-run day2 artifacts.

## v0.7.4 Long/Mid/Short Scoring System

v0.7.4 consumes v0.7.3 strict-universe feature artifacts and writes score artifacts under `data/equity_scores/daily/YYYY-MM-DD/`, reports under `outputs/equity_scores/daily/YYYY-MM-DD/`, and a scoring audit under `data/equity_data_quality/` and `outputs/audit/`.

The score set is `LongScore`, `MidScore`, `ShortScore`, `RiskScore`, `LiquidityScore`, `IndustryScore`, `FundamentalScore`, and `CompositeOpportunityScore`. Scores, percentiles, and ranks are relative research metrics only. They are not recommendations, buy/sell signals, candidate pools, watchlists, portfolio allocations, broker instructions, real orders, profit guarantees, live readiness, or official forward dry-run day2 artifacts.

v0.7.5 consumes these scores for candidate generation. v0.7.6 consumes candidates for research-only virtual portfolios.

## v0.7.5 Candidate Generation System

v0.7.5 consumes v0.7.4 score artifacts and writes candidate artifacts under `data/equity_selection/daily/YYYY-MM-DD/`, reports under `outputs/equity_selection/daily/YYYY-MM-DD/`, and a candidate generation audit under `data/equity_data_quality/` and `outputs/audit/`.

The candidate set includes long candidates, mid candidates, short candidates, an extended watch pool, multi-horizon candidates, risk-downgraded candidates, reason breakdown, generation summary, and manifest. Selection uses ranks and percentiles with risk, liquidity, confidence, and overheat gates. The output is a research candidate package only.

Candidates are not investment advice, not buy/sell signals, not order instructions, not virtual portfolios, not broker instructions, not real orders, not profit guarantees, not live readiness, and not official forward dry-run day2 artifacts.

v0.7.6 consumes these candidates for virtual portfolio construction. Daily AI stock selection briefing remains deferred to v0.7.7.

## v0.7.6 Virtual Portfolio Construction

v0.7.6 consumes v0.7.5 candidate artifacts and writes virtual portfolio artifacts under `data/equity_portfolios/daily/YYYY-MM-DD/`, reports under `outputs/equity_portfolios/daily/YYYY-MM-DD/`, and a virtual portfolio construction audit under `data/equity_data_quality/` and `outputs/audit/`.

The portfolio set includes `long_virtual_portfolio`, `mid_virtual_portfolio`, `short_virtual_portfolio`, portfolio target weights, industry exposure, risk/liquidity summary, manifest, reports, and audit. The portfolios are long-only, unlevered, derivatives-free, and research-only.

Virtual portfolios are not real portfolios. Virtual target weights are not buy/sell signals, not broker order previews, not real-account rebalance instructions, not broker instructions, not real orders, not profit guarantees, not live readiness, and not official forward dry-run day2 artifacts.

Daily AI stock selection briefing remains deferred to v0.7.7.

## Boundary
- No real trading.
- No broker connection.
- No real orders.
- No third-party trading code merged into the main flow.
- No LLM direct trading decision.
- No model profit guarantee.
- ETF forward dry-run status unchanged.
- `run-daily` not called.
- Data foundation only until coverage and schema audits pass.
- v0.7.2 filter buckets are not recommendations and are not candidate lists.
- v0.7.3 feature tables are not scores, recommendations, candidate lists, watchlists, portfolios, or order plans.
- v0.7.4 score tables are not recommendations, candidate lists, watchlists, portfolios, buy/sell signals, or order plans.
- v0.7.5 candidate pools are not recommendations, buy/sell signals, portfolio allocations, order plans, broker instructions, or profit guarantees.
- v0.7.6 virtual portfolios are not real portfolios, buy/sell signals, order previews, broker instructions, real orders, or profit guarantees.
- Public data may be delayed or partial; limitations are evidence, not recommendations.
