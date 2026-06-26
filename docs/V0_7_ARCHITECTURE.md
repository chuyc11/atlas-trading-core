# v0.7 Architecture

Positioning: A-share full-market AI multi-horizon stock selection and virtual portfolio tracking system

## Data Flow
- Public/local provider adapters
- A-share universe and trading calendar
- daily price, adjusted price, daily basic, industry, and basic financial data panels
- coverage audit and schema audit
- tradability/liquidity/risk filters
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
  Q --> B["Tradability / risk / liquidity filters"]
  B --> C["Long / Mid / Short features"]
  C --> D["LongScore / MidScore / ShortScore"]
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
- Public data may be delayed or partial; limitations are evidence, not recommendations.
