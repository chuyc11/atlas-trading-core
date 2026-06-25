# Historical Data Packages

v0.5.7 acquires authorized historical research data for replay, coverage, PIT audit, and global-briefing proxy construction. User authorized historical data access is available for this phase. Historical data authorization is not trading authorization.

The workflow does not connect to a broker, does not place real orders, does not download broker account/order/trade/position/margin data, does not start or validate forward dry-run, does not use labels, ML shadow, experiments, promotion, RL, or LLM trading decisions, and does not write the main orders/trades/portfolio/accounts ledgers.

## Package Matrix

| Package | Purpose | Source priority | Output path | Required | Production relevance | Limitations |
|---|---|---|---|---|---|---|
| `HIST-ETF-OHLCV-CN-HK-V1` | Tradable ETF OHLCV for historical replay prices, valuation, ETF coverage audit, and benchmark comparison | authorized local export, Yahoo query or equivalent authorized market data source, fixture for tests | `data/market/historical/authorized/HIST-ETF-OHLCV-CN-HK-V1.csv` | yes, critical | Replay price base for China/HK ETF research | Historical data only; not order data; not proof of tradability or execution quality |
| `HIST-BENCHMARK-INDEX-CN-HK-V1` | Benchmark OHLCV and synthetic cash comparison series | authorized local export, Yahoo query or equivalent authorized market data source, fixture for tests | `data/market/historical/authorized/HIST-BENCHMARK-INDEX-CN-HK-V1.csv` | yes, critical | Benchmark context for replay and reports | Benchmark coverage does not prove strategy effectiveness |
| `HIST-FX-USDCNY-V1` | USD/CNY daily risk input | authorized local export, FRED `DEXCHUS`, other configured authorized source, fixture for tests | `data/global_briefing/authorized/packages/HIST-FX-USDCNY-V1.csv` | yes, critical with VIX alternative | Critical macro risk input for proxy construction | Public fallback may be a market proxy; source warnings must be reviewed |
| `HIST-GLOBAL-RISK-VIX-V1` | VIX daily close for global risk | authorized local export, FRED `VIXCLS`, Cboe VIX file, fixture for tests | `data/global_briefing/authorized/packages/HIST-GLOBAL-RISK-VIX-V1.csv` | yes, critical with FX alternative | Critical risk input for proxy construction | VIX is a proxy, not a China-specific signal |
| `HIST-RATES-LIQUIDITY-V1` | Rates and liquidity pressure inputs | authorized local export, FRED rates/funding series, public market-yield proxy fallback, fixture for tests | `data/global_briefing/authorized/packages/HIST-RATES-LIQUIDITY-V1.csv` | yes, non-critical | Supports liquidity and rates pressure fields in the proxy package | Missing exact China money-market series is a limitation when unavailable |
| `HIST-COMMODITY-INFLATION-RISK-V1` | Commodity and inflation risk inputs | authorized local export, FRED commodity series, public futures proxy fallback, fixture for tests | `data/global_briefing/authorized/packages/HIST-COMMODITY-INFLATION-RISK-V1.csv` | yes, non-critical | Supports commodity inflation pressure in the proxy package | Futures proxies are not full inflation models |
| `HIST-POLICY-UNCERTAINTY-EPU-V1` | Policy uncertainty and EPU inputs | authorized local export, authorized EPU API config, FRED-compatible EPU series, authorized policy-uncertainty proxy from VIX/FX, fixture for tests | `data/global_briefing/authorized/packages/HIST-POLICY-UNCERTAINTY-EPU-V1.csv` | yes, non-critical | Optional input for policy uncertainty, risk_off, and EPU fields | If official EPU is unavailable, partial package or policy-uncertainty proxy is allowed when clearly marked; missing subseries are package-level warnings |
| `HIST-OECD-CLI-MACRO-CYCLE-V1` | OECD CLI macro cycle inputs | authorized local export, authorized OECD API config, OECD public API if configured, authorized macro-cycle proxy, fixture for tests | `data/global_briefing/authorized/packages/HIST-OECD-CLI-MACRO-CYCLE-V1.csv` | yes, non-critical | Optional input for macro cycle pressure | If official OECD CLI is unavailable, authorized macro-cycle proxy is allowed only when `official_oecd_cli=false`, `macro_cycle_proxy=true`, and `not_official_oecd_cli=true` |
| `HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1` | Optional authorized production global-briefing historical signal package | `GB_AUTH_PACKAGE_PATH`, authorized GB API config, local authorized export | `data/global_briefing/authorized/packages/HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1.raw` and `data/global_briefing/normalized/HIST-AUTH-GLOBAL-BRIEFING-SIGNALS-V1.normalized.jsonl` | optional | Separately reports whether production global-briefing package is configured and validated | If not configured, status is `not_configured`, blocking is false, and `production_global_briefing_package_validated=false` |
| `GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1` | Unified global-briefing-compatible proxy package built from macro/risk packages C-H | Built locally from downloaded or loaded historical packages | `data/global_briefing/authorized/packages/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.jsonl` and `data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl` | yes, derived | Provides replay-compatible proxy signals for isolated research replay | Proxy package is not an internal global-briefing signal package and not production signal validation |

## Required Reports

- Source resolution: `data/system/historical_data_source_resolution.json`, `outputs/system/HISTORICAL_DATA_SOURCE_RESOLUTION.md`
- Download manifest: `data/system/historical_data_download_manifest.json`, `outputs/system/HISTORICAL_DATA_DOWNLOAD_MANIFEST.md`
- Normalization summary: `data/system/historical_package_normalization_summary.json`, `outputs/system/HISTORICAL_PACKAGE_NORMALIZATION_REPORT.md`
- Quality audit: `data/system/historical_data_quality_audit.json`, `outputs/audit/HISTORICAL_DATA_QUALITY_AUDIT.md`
- Full proxy replay workflow: `data/replays/global_briefing/full_historical_proxy_workflow-START-END.json`, `outputs/replays/global_briefing/FULL_HISTORICAL_PROXY_WORKFLOW-START-END.md`
- Acquisition report: `data/system/historical_data_acquisition_report.json`, `outputs/system/HISTORICAL_DATA_ACQUISITION_REPORT.md`
- Acquisition audit: `data/system/historical_data_acquisition_audit.json`, `outputs/audit/HISTORICAL_DATA_ACQUISITION_AUDIT.md`
- Historical warning inventory: `data/system/historical_warning_inventory.json`, `outputs/system/HISTORICAL_WARNING_INVENTORY.md`
- Gap closure workflow: `data/system/historical_data_gap_closure_workflow.json`, `outputs/system/HISTORICAL_DATA_GAP_CLOSURE_WORKFLOW.md`
- Gap closure report: `data/system/historical_data_gap_closure_report.json`, `outputs/system/HISTORICAL_DATA_GAP_CLOSURE_REPORT.md`
- Gap closure audit: `data/system/historical_data_gap_closure_audit.json`, `outputs/audit/HISTORICAL_DATA_GAP_CLOSURE_AUDIT.md`

## Boundary

- Historical replay is not forward dry-run validation.
- Historical replay is not strategy effectiveness proof.
- The system is not live trading ready.
- Main ledger paths are not written.
- `run-daily` is not called.
- Production global-briefing package status must be separately reported.
- The unified proxy package is research input only and must not be described as internal global-briefing output.
- EPU policy-uncertainty proxy must not be described as official EPU data.
- OECD macro-cycle proxy must not be described as official OECD CLI data.
