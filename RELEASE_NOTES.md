# Release Notes

## v0.7.2-a-share-tradable-universe-filter

This release adds the A-share tradable universe filter on top of the v0.7.1.2 full-market historical panels. It builds daily strict/caution/excluded/unknown buckets and an audit gate for future feature engineering. It is not a stock scoring, candidate generation, watchlist, portfolio, broker, or trading stage.

Includes:

- A-share tradable universe filter
- strict/caution/excluded/unknown universe buckets
- listing-age filter based on trading calendar age
- suspension and missing-price filter
- liquidity filter using 20d/60d average amount with explicit amount estimation flags
- market-cap filter with daily basic snapshot fallback when historical market-cap fields are unavailable
- low-price and price-sanity filters
- one-word limit up/down risk filter
- data coverage filter for 20d/60d/120d/250d history
- filter reason taxonomy and reason breakdown artifacts
- owner-facing tradable universe report
- tradable universe audit with boundary and forbidden-positive-wording checks

Audited result for `as_of_date=2026-06-26`:

- equity master symbols: 5867
- input symbols: 5867
- strict tradable count: 3676
- caution count: 0
- excluded count: 2191
- unknown status count: 0
- audit overall_passed=true
- blocking reasons: none
- warnings: 1
- recommended next version: `v0.7.3-a-share-multi-horizon-feature-engineering`

Boundary:

- no LongScore, MidScore, ShortScore, RiskScore, or LiquidityScore generated
- no candidates generated
- no watchlist generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no model profit guarantee
- live trading readiness remains false

Validation: 988 tests passed, 1 skipped.

## v0.7.1.2-a-share-historical-data-provider-expansion

This release resolves the v0.7.1.1 historical price coverage blocker by expanding the A-share historical backfill path from a limited/sample run to a full-market symbol queue sourced from `data/equity_universe/equity_master.parquet`.

Includes:

- root-cause diagnostic for the v0.7.1.1 10-symbol fail-closed result
- full-market A-share historical backfill symbol queue
- Eastmoney historical kline provider expansion with AkShare, BaoStock, Tushare, and local fallback adapters
- checkpoint/resume support for long full-market historical backfills
- per-batch manifests and per-symbol backfill manifest
- global coverage ratios against equity master and backfill queue
- readiness recommendation fix: failed readiness recommends `v0.7.1.3-a-share-historical-data-source-upgrade`, not `v0.7.2`
- updated historical coverage and feature-readiness audits

Audited coverage:

- equity master symbols: 5867
- backfill queue symbols: 5516
- price history symbols: 5516
- price history date range: `2021-01-04` to `2026-06-26`
- price history trading days: 1326
- symbols with 20d / 60d / 120d / 250d / 3y / 5y history: 5509 / 5474 / 5441 / 5379 / 5132 / 4458
- adjusted price symbols: 5516
- daily basic symbols: 5516
- financial symbols: 5211
- price history coverage vs equity master: 0.940174
- price history coverage vs queue: 1.0
- daily basic coverage vs equity master: 0.940174
- financial coverage vs equity master: 0.888188
- historical panel coverage audit overall_passed=true
- feature readiness audit overall_passed=true
- blocking reasons: none

Boundary:

- no stock scores generated
- no candidates generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no third-party code merged into the main flow
- no model profit guarantee
- live trading readiness remains false
- recommended next version is `v0.7.2-a-share-tradable-universe-filter`

Validation: 976 tests passed, 1 skipped.

## Unreleased: v0.7.1.1-a-share-historical-panel-backfill fail-closed

This implementation adds the A-share historical panel backfill workflow and readiness audits, but it is not released as a success tag because the current public historical provider run did not satisfy the minimum historical coverage gate.

Implemented:

- historical backfill plan
- daily price history panel writer
- adjusted price history panel writer with raw fallback labeling
- daily basic history panel writer with nullable field coverage
- partial quarterly financial history panel writer
- historical panel coverage audit
- feature readiness audit
- CLI commands for individual and one-command historical backfill
- documentation for historical backfill and feature readiness

Current fail-closed evidence:

- price history symbols: 10
- price history trading days: 841
- symbols with 120d history: 10
- symbols with 250d history: 10
- financial symbols: 1237
- financial quarter coverage ratio: 0.028407
- historical panel coverage audit overall_passed=false
- feature readiness audit overall_passed=false
- blocking reasons include `price_history_symbols_minimum=false`, `symbols_with_120d_history_minimum=false`, and `symbols_with_250d_history_minimum=false`
- no stock scores generated
- no candidates generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no model profit guarantee
- no live trading readiness claim

Validation: 961 tests passed, 1 skipped.

## v0.7.1-a-share-full-market-data-ingestion

This release adds the A-share full-market data ingestion foundation for the future AI stock selection line. It writes local master, calendar, market, industry, fundamental, source-manifest, coverage-audit, and schema-audit artifacts. It does not generate stock scores, candidates, watchlists, virtual portfolios, broker instructions, real orders, or official forward dry-run day2 artifacts.

Includes:

- A-share equity master for SSE/SZSE/BSE
- A-share trading calendar foundation
- daily price panel ingestion
- adjusted price panel ingestion with coverage tracking
- daily basic panel ingestion
- industry classification ingestion
- basic financials ingestion
- data source manifest
- coverage audit
- schema audit
- public provider fallback strategy documentation
- A-share data ingestion, schema, and quality-audit documentation

Audited & Validated scope:

- provider selected: `qstock_reference_public_http`
- source rows available: 5867
- source raw total: 5867
- source raw coverage ratio: 1.0
- equity master symbols: 5867
- observed exchanges: BSE, SSE, SZSE
- daily price symbols: 5513
- adjusted price symbols: 5513
- daily basic symbols: 5867
- industry symbols: 5867
- financial symbols: 5867
- min daily price date: `2026-06-26`
- max daily price date: `2026-06-26`
- trading days in calendar artifact: 282
- coverage audit passed with no blocking reasons
- schema audit passed with no blocking reasons
- warnings: raw adjusted-price fallback, board-level industry fallback, nullable basic financial numeric fields, and 354 master symbols missing daily price in the current public snapshot
- no stock scores generated
- no candidates generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no third-party code merged into the main flow
- model profit not guaranteed
- recommended next version is `v0.7.2-a-share-tradable-universe-filter`

Validation: 951 tests passed, 1 skipped.

## v0.7.0-external-project-intake-and-a-share-selection-plan

This release opens the A-share full-market AI multi-horizon stock selection planning line. It downloads external research repositories into ignored `external_research/`, scans their README/license/source structure, writes an external intake report, generates an A-share full-market selection plan, produces a reuse matrix, and writes the v0.7 architecture and roadmap summary.

Includes:

- external research download script
- `external-project-intake` CLI
- `data/system/external_project_intake_report.json`
- `outputs/system/EXTERNAL_PROJECT_INTAKE_REPORT.md`
- `outputs/system/V0_7_ROADMAP_SUMMARY.md`
- `docs/A_SHARE_FULL_MARKET_AI_STOCK_SELECTION_PLAN.md`
- `docs/EXTERNAL_PROJECT_INTAKE.md`
- `docs/EXTERNAL_PROJECT_REUSE_MATRIX.md`
- `docs/V0_7_ARCHITECTURE.md`

Audited & Validated scope:

- external repos downloaded: 11
- AlphaSift classified A for full-market scanning, candidate ranking, and T+N evaluation reference
- qstock classified A for data adapters, WenCai-style screening, RPS/MM trend, fundamentals, and capital-flow reference
- daily_stock_analysis classified A for daily briefing, LLM summary, and notification reference
- guiwzh/stock classified A for long/short score weighting and stock score report reference
- Qlib classified B for ML workflow, RankIC/IC, and walk-forward evaluation reference
- AlphaEvo classified B for scoring weight optimization research
- easytrader, easyquotation, and easyquant classified D for future broker/quote/event adapter research
- THSTrader classified D for future Tonghuashun simulated trading adapter research
- zvt included as optional B/C architecture reference
- no third-party trading code merged into the main flow
- ETF forward dry-run status unchanged
- day2 not executed
- run-daily not called
- broker not connected
- real orders not placed
- LLM not used for trading decisions
- model profit not guaranteed
- recommended next version is `v0.7.1-a-share-full-market-data-ingestion`

Validation: 938 tests passed, 1 skipped.

## v0.6.3.2-forward-dry-run-day1-owner-report-pack

This release adds an owner-facing day1 report pack for the completed virtual forward dry-run day 1. It does not execute day2, does not execute day3, does not call `run-daily`, does not download real-time market data, does not call external market APIs, does not connect a broker, does not place real orders, and does not write main orders/trades/portfolio/accounts.

Includes:

- day1 owner report scope plan
- day1 owner summary report
- day1 strategy signal explanation
- day1 virtual order and fill report
- day1 isolated ledger report
- day1 data reproducibility appendix
- day1 continuation blocker note
- day1 owner report pack summary
- day1 owner report audit

Audited & Validated scope:

- day1 completed
- day1 as_of_date is `2026-06-25`
- `strategies_total=3`
- `strategies_generated=3`
- virtual order preview produced 16 orders
- virtual execution produced 16 fills and 0 rejects
- owner report pack complete
- owner report audit passed with no blocking reasons
- day2 not executed
- day3 not executed
- run-daily not called
- real-time market data not downloaded
- external API not called
- main orders/trades/portfolio/accounts not written
- broker not connected
- real orders not placed
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not strategy effectiveness proof
- not full forward dry-run validation
- not live trading readiness
- recommended next version is `v0.6.3.3-forward-dry-run-data-horizon-extension`

Validation: 935 tests passed, 1 skipped.

## v0.6.3.1-forward-dry-run-day1-continuation-artifacts

This release absorbs the v0.6.4 blocking preflight and materializes the missing v0.6.3 day1 continuation artifacts required before a future day2 continuation attempt. It does not execute day2, does not execute day3, does not call `run-daily`, does not connect a broker, does not place real orders, and does not write main orders/trades/portfolio/accounts.

Includes:

- day1 continuation gap analysis
- day1 artifact manifest
- day1 reproducibility manifest
- day2 readiness packet
- day2 continuation gate preview
- day1 continuation artifact audit
- day1 continuation reclassification v0631

Audited & Validated scope:

- v0.6.4 blocking preflight absorbed
- missing continuation artifact gap resolved
- `day1_artifact_manifest` generated
- `day1_reproducibility_manifest` generated
- `day2_readiness_packet` generated
- `day2_continuation_gate_preview` generated
- continuation artifact audit passed with no blocking reasons
- `continuation_artifact_gap_resolved=true`
- `remaining_continuation_artifact_gap_count=0`
- `day2_blocker_count=0`
- recommended next version is `v0.6.4-forward-dry-run-day2-continuation`
- day2 not executed
- day3 not executed
- run-daily not called
- main orders/trades/portfolio/accounts not written
- broker not connected
- real orders not placed
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not strategy effectiveness proof
- not full forward dry-run validation
- not live trading readiness

Validation: full pytest passed with 1 skipped.

## v0.6.3-forward-dry-run-day1-executed-audited

This release executes virtual isolated forward dry-run day 1 after owner authorization materialization. It starts the forward dry-run ledger for day 1 only. It does not call `run-daily`, does not connect a broker, does not place real orders, does not write the main orders/trades/portfolio/accounts ledger, and does not complete the 30-day forward dry-run.

Includes:

- day1 pre-execution gate with git-clean, authorization, data, protected-path, and no broker/live guard checks
- day1 input snapshot from local authorized historical data as of 2026-06-25
- day1 baseline strategy signals for all three baseline strategies
- day1 virtual order preview with T+1, tradability, lot, and cost checks
- day1 virtual execution result in `forward_dry_run_virtual` mode
- isolated forward dry-run ledger snapshot
- day1 risk and boundary report
- day1 operator report
- post-execution audit
- forward dry-run status
- day1 blocker reclassification v063

Audited & Validated scope:

- pre-execution gate passed
- latest eligible local as-of date: 2026-06-25
- `strategies_total=3`
- `strategies_generated=3`
- virtual order preview produced 16 orders and 0 rejects
- virtual execution produced 16 fills and 0 rejects
- `forward_dry_run_started=true`
- `forward_dry_run_days_completed=1`
- `next_day_index=2`
- isolated forward dry-run ledger written
- main ledger not written
- broker not connected
- real orders not placed
- labels not used
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not full forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness

Validation: 890 tests passed, 1 skipped.

## v0.6.2.1-owner-manual-confirmation-materialized

This release materializes owner manual confirmation for the forward dry-run start authorization flow. It makes the system eligible for a future day1 prompt request, but it does not start forward dry-run day 1, does not call `run-daily`, does not generate a day1 execution prompt, and does not write the main ledger.

Includes:

- owner manual confirmation record
- completed manual confirmation checklist v2
- authorized owner packet for day1 prompt generation
- start gate revalidation
- day1 prompt eligibility revalidation
- authorization materialization audit
- day1 blocker reclassification v0621

Audited & Validated scope:

- `manual_confirmation_complete=true`
- `forward_dry_run_start_authorized=true`
- `day1_prompt_eligible=true`
- `day1_prompt_generated=false`
- `day1_start_allowed=false`
- `run-daily` not called
- forward dry-run not started
- main ledger not written
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness

Validation: 877 tests passed, 1 skipped.

## v0.6.2-forward-dry-run-start-authorization-pack-audited

This release creates the fail-closed start authorization pack required before any future forward dry-run day 1. It does not start forward dry-run, does not call `run-daily`, does not write the main orders/trades/portfolio/accounts ledger, and does not generate an executable day1 prompt.

Includes:

- forward dry-run authorization scope plan
- start prerequisite inventory
- current daily workflow readiness snapshot
- manual confirmation checklist v2
- owner authorization packet
- start gate validator
- run-daily command preview metadata
- day1 prompt eligibility report
- start authorization audit
- day1 blocker reclassification v062

Audited & Validated scope:

- technical prerequisites are present
- manual confirmation defaults false
- owner authorization defaults false
- `day1_start_allowed=false`
- `day1_prompt_eligible=false`
- `day1_prompt_generated=false`
- `run-daily` not called
- forward dry-run not started
- main ledger not written
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness

Validation: 862 tests passed, 1 skipped.

## v0.6.1-daily-workflow-binding-audited

This release binds the v0.6.0 baseline strategy pack and v0.5.9 virtual execution rules into a repeatable daily research preview workflow. Daily workflow binding is research-only preview infrastructure and does not start forward dry-run. It uses local authorized historical daily data snapshots, does not download real-time market data, does not call `run-daily`, and does not write the main orders/trades/portfolio/accounts ledger.

Includes:

- daily workflow scope plan
- daily market data snapshot contract
- latest available trading date detection from local data
- daily data freshness/completeness audit
- daily input freeze manifest with file hashes
- daily baseline signal binding
- daily order preview binding
- daily isolated execution preview
- daily report packet
- protected path residue scanner
- daily workflow audit
- day1 blocker reclassification v061

Audited & Validated scope:

- `daily-workflow-scope-plan` confirmed v0.6.0 baseline strategy pack completeness and kept day 1 disallowed.
- `daily-market-data-snapshot --as-of-date 2024-12-31` generated a local historical snapshot without external download.
- `audit-daily-data-quality` passed with universe coverage complete and risk proxy available; missing direct benchmark rows for CSI500, CSI1000, and CHINEXT are recorded as warnings.
- `daily-input-freeze-manifest` recorded hashes for market data, benchmark data, risk proxy, baseline contracts, strategy registry, virtual execution, calendar, price status, lot position, cost contract, data quality audit, and snapshot.
- `daily-baseline-signals --strategy all` generated daily signals for all three baseline strategies.
- `daily-order-preview --strategy all --execution-mode isolated` generated preview-only order proposals with `executed=false`.
- `daily-isolated-execution-preview --execution-mode isolated` generated state-free preview fills, rejects, costs, and valuation estimates with `execution_mode=isolated_preview`.
- `daily-report-packet` generated the operator-facing research preview packet with explicit non-claims.
- `protected-path-residue-scan` classified ignored runtime residue as nits and produced blocker count 0.
- `audit-daily-workflow` passed with no blocking reasons and recommends `v0.6.2-forward-dry-run-start-authorization-pack`.
- `reclassify-day1-blockers-after-daily-workflow` kept `day1_start_allowed=false`, `manual_confirmation_complete=false`, and `forward_dry_run_start_authorized=false`.
- `run-daily` was not called.
- Forward dry-run was not started or validated.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Labels, ML shadow, LLM, RL, experiments, and promotion outputs were not used as authorization.
- Promotion was not triggered.
- Historical preview output is not strategy effectiveness proof.
- This release is not forward dry-run validation and not live trading readiness.

Validation: 839 tests passed, 1 skipped.

## v0.6.0-baseline-strategy-pack-audited

This release adds a research-only baseline strategy pack for future forward dry-run preparation. Baseline strategy pack is research-only and does not start forward dry-run. It does not call `run-daily`, does not write the main orders/trades/portfolio/accounts ledger, does not use labels, ML shadow, LLM, RL, experiments, or promotion outputs as authorization, and does not prove strategy effectiveness or certify live trading readiness.

Includes:

- baseline strategy scope plan
- baseline strategy contract
- baseline strategy registry and parameter versions
- `equal_weight_etf_rotation`
- `momentum_risk_adjusted_rotation`
- `defensive_cash_rotation`
- PIT-safe baseline strategy signals
- baseline order previews with `preview_only=true` and `executed=false`
- isolated baseline strategy replay using v0.5.9 virtual execution rules
- benchmark comparison
- baseline strategy reports
- baseline strategy pack summary
- baseline strategy pack audit
- day1 blocker reclassification v060

Audited & Validated scope:

- `baseline-strategy-scope-plan` confirmed v0.5.9 execution blockers are closed and v0.6.0 is not day 1.
- `baseline-strategy-contract` generated machine-readable input, output, PIT, forbidden-input, forbidden-claim, and boundary requirements.
- `baseline-strategy-registry` registered three deterministic rule-based strategies and parameter versions.
- `generate-baseline-strategy-signals --strategy all --start-date 2024-01-02 --end-date 2024-12-31` generated PIT-safe after-close signals with T+1 earliest execution.
- `build-baseline-order-preview --strategy all --execution-mode isolated` generated preview-only proposals.
- `replay-baseline-strategy --strategy all --execution-mode isolated` wrote isolated strategy replay orders/trades/portfolio/valuations under `data/replays/strategies/`.
- `compare-baseline-strategy-benchmarks --strategy all` generated benchmark comparison for CSI300, CSI500, CSI1000, CHINEXT, HSI, HSTECH, CASH, and EQUAL_ETF.
- `baseline-strategy-report --strategy all` generated one report per strategy with explicit non-claims.
- `baseline-strategy-pack-summary` passed with `all_strategies_complete=True`.
- `audit-baseline-strategy-pack` passed with no blocking reasons.
- `reclassify-day1-blockers-after-baseline-strategies` produced `updated_day1_blocker_count=0` and recommends `v0.6.1-daily-workflow-binding`.
- `run-daily` was not called.
- Forward dry-run was not started or validated.
- Main orders/trades/portfolio/accounts ledgers were not written.
- ML shadow was not used as authorization.
- LLM was not used for trading decision.
- RL was not used.
- Promotion was not triggered.
- Historical performance is not strategy effectiveness proof.
- This release is not live trading readiness.

Validation: 811 tests passed, 1 skipped.

## v0.5.9-ashare-execution-rules-hardened

This release hardens A-share / ETF virtual execution rules for future forward dry-run preparation. v0.5.9 hardens virtual execution rules but does not start forward dry-run. It does not call `run-daily`, does not write the main orders/trades/portfolio/accounts ledger, does not prove strategy effectiveness, and does not certify live trading readiness.

Includes:

- A-share / ETF trading calendar contract for SSE / SZSE / HKEX
- T-day signal / T+1 execution semantics
- suspension / missing price / limit up / limit down handling
- ST / new listing handling
- board lot / odd lot rules
- fee / tax / slippage model
- cash / position / available shares accounting
- virtual execution contract
- isolated ledger invariant audit
- execution-aware replay smoke
- day1 blocker reclassification

Audited & Validated scope:

- `ashare-execution-gap-plan` read v0.5.8.1 blocker artifacts and targeted three execution blockers.
- `ashare-trading-calendar-audit` passed for SSE, SZSE, HKEX, explicit holidays, weekends, and HKEX/A-share calendar differences.
- `execution-timeline-contract` rejects same-day execution for T-day close signals and rejects future prices.
- `ashare-price-status-contract` handles suspended, missing price, limit up, limit down, ST, new listing, delisting risk, and unknown status fail-closed.
- `ashare-lot-and-position-contract` defines board lot, odd lot sell, T+1 available shares, and cash/position invariants.
- `ashare-execution-cost-contract` defines commission, minimum commission, stamp duty, slippage, and PIT-safe fill price rules.
- `virtual-execution-contract` integrates calendar, T+1, tradability, lot, cash/position, costs, reject reasons, fill reasons, isolated output paths, and protected path guard.
- `audit-isolated-ledger-invariants` passed.
- `execution-aware-replay-smoke` passed in isolated mode.
- `reclassify-day1-blockers-after-execution-hardening` closed the three execution blockers and recommends `v0.6.0-baseline-strategy-pack`.
- `audit-ashare-execution-rules` passed with no blocking reasons.
- `run-daily` was not called.
- Forward dry-run was not started or validated.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Labels, ML shadow, experiments, LLM, RL, and promotion outputs were not used as authorization.

Validation: 787 tests passed, 1 skipped.

## v0.5.8.1-plan-alignment-and-mvp-gap-audited

This patch release adds plan alignment and MVP gap audit artifacts. Plan alignment is an audit, not day 1 authorization. It does not start forward dry-run, does not call `run-daily`, and does not write the main orders/trades/portfolio/accounts ledger.

Includes:

- plan checklist extractor
- MVP requirement map
- artifact coverage scanner
- MVP gap classifier
- day-1 blocker classifier
- next work register
- plan alignment audit

Audited & Validated scope:

- `plan-checklist` extracted R001-R024 MVP requirements.
- `mvp-requirement-map` mapped each requirement to candidate module, CLI, test, artifact, report, audit, doc, or release-tag evidence.
- `artifact-coverage-scanner` scanned repo artifacts as metadata only.
- `classify-mvp-gaps` classified all 24 requirements.
- `classify-day1-blockers` generated day-1 blocker status while keeping day 1 disallowed by default.
- `next-work-register` generated the recommended next version.
- `audit-plan-alignment` passed with `overall_passed=True` and no blocking reasons.
- `run-daily` was not called.
- Forward dry-run was not started.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Labels were not used as authorization.
- ML shadow was not used as day-1 authorization.
- LLM was not used for trading decision.
- RL was not used.
- Promotion was not triggered.
- Historical performance is not strategy effectiveness proof.

Validation: 755 tests passed, 1 skipped.

## v0.5.8-day0-operational-readiness-audited

This release adds the day-0 operational readiness pack for a future 30 trading-day forward dry-run. Day-0 readiness does not start forward dry-run. Historical data authorization is not trading authorization.

Includes:

- day-0 data freeze manifest
- accepted warning register
- blocking condition register
- run-daily preflight checklist with command preview only
- manual confirmation packet with all confirmation fields default false
- forward dry-run operating calendar and daily log template
- day-0 readiness report
- day-0 readiness audit

Audited & Validated scope:

- `day0-data-freeze` generated frozen input package records and accepted known EPU/OECD limitations.
- `day0-warning-register` classified remaining v0.5.7.1 warnings and produced `blocking_count=0`.
- `day0-blocking-conditions` produced `current_blocking_count=0` while keeping manual confirmation required.
- `day0-run-daily-preflight` generated a preview-only `run-daily` command with `executed=false`.
- `day0-manual-confirmation-packet` kept `manual_confirmation_complete=false` and `forward_dry_run_start_authorized=false`.
- `forward-dry-run-operating-calendar` generated a template-only 30 day operating calendar and daily log template.
- `day0-readiness-report` produced `overall_status=ready_for_manual_confirmation`.
- `audit-day0-readiness` passed with `overall_passed=True` and no blocking reasons.
- EPU partial limitation is recorded.
- OECD macro-cycle proxy limitation is recorded and not described as official OECD CLI.
- Internal global-briefing historical package remains `not_configured`.
- Proxy package is not an internal global-briefing signal.
- Main orders/trades/portfolio/accounts ledgers were not written.
- `run-daily` was not called.
- Labels, ML shadow, experiments, promotion outputs, broker/live integration, RL, and LLM trading decisions were not used.

Boundaries remain strict: day-0 readiness is not forward dry-run validation, not strategy effectiveness proof, not live trading readiness, not trading authorization, not broker integration, and not promotion approval.

Validation: 737 tests passed, 1 skipped.

## v0.5.7.1-historical-data-gap-closure-audited

This patch release closes v0.5.7 historical research data gaps and reduces warning noise for the authorized full historical proxy replay path. Historical data authorization is not trading authorization.

Includes:

- historical warning inventory with category, severity, grouped counts, and fix status
- EPU package repair through authorized/local/API/FRED-compatible sources, with policy-uncertainty proxy fallback when official source access is unavailable
- OECD CLI repair through authorized/local/API sources, with authorized macro-cycle proxy fallback explicitly marked as not official OECD CLI
- full historical proxy package rebuild with EPU and macro-cycle fields
- normalized proxy package rebuild and signal contract validation
- full historical proxy replay grouped warning output with raw warning count preserved
- gap closure workflow, gap closure report, and gap closure release audit

Audited & Validated scope:

- `close-historical-data-gaps --start-date 2018-01-01 --end-date latest --replay-start-date 2024-01-02 --replay-end-date 2024-12-31 --min-coverage 0.80 --continue-on-error` passed.
- Available packages improved from 6/9 to at least 8/9 while keeping the optional authorized global-briefing historical signal package separately reported.
- EPU was repaired or represented by a clearly marked policy-uncertainty proxy.
- OECD CLI was repaired or represented by a clearly marked authorized macro-cycle proxy that is not official OECD CLI.
- `historical-warning-inventory` generated JSON and Markdown with unknown warnings reduced to zero.
- `run-full-historical-proxy-replay` retained raw warning counts and displayed grouped warnings.
- `historical-data-gap-closure-report` generated JSON and Markdown.
- `audit-historical-data-gap-closure` passed with `overall_passed=True` and no blocking reasons.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Isolated replay artifacts were written under `data/replays/global_briefing/`.
- `run-daily` was not called.
- Labels, ML shadow, experiments, promotion outputs, broker/live integration, RL, and LLM trading decisions were not used.
- Forward dry-run was not started or validated.

Boundaries remain strict: this is historical data gap closure only, not broker integration, not live trading, not forward dry-run validation, not strategy effectiveness proof, not live trading readiness, not production global-briefing package validation, and not promotion approval.

Validation: 716 tests passed, 1 skipped.

## v0.5.7-authorized-full-historical-data-acquisition-audited

This release adds authorized full historical data package acquisition for the global-briefing research replay path. It downloads or loads historical packages, normalizes them, builds a unified proxy package, audits quality, runs isolated proxy replay, and produces acquisition reports. Historical data authorization is not trading authorization.

Includes:

- authorized full historical data package acquisition
- ETF OHLCV package
- benchmark index package
- FX / USD-CNY package
- VIX / global risk package
- rates / liquidity package
- commodity / inflation risk package
- policy uncertainty / EPU package status and warnings
- OECD CLI / macro cycle package status and warnings
- optional authorized global-briefing historical signal package status
- unified global-briefing-compatible proxy package
- historical data quality audit
- full historical proxy isolated replay workflow
- historical data acquisition report
- historical data acquisition audit

Audited & Validated scope:

- `download-historical-data-packages --start-date 2018-01-01 --end-date latest --continue-on-error` generated package manifests and provenance.
- ETF, benchmark, FX/USD-CNY, VIX, rates/liquidity, and commodity/inflation packages downloaded with checksums.
- EPU and OECD CLI package attempts failed soft with explicit warnings.
- Authorized global-briefing historical signal package was `not_configured` and non-blocking.
- `normalize-historical-data-packages` built and validated `GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1`.
- `audit-historical-data-quality` passed with `overall_passed=True`.
- `run-full-historical-proxy-replay --execution-mode isolated` completed with `overall_status=research_review_ready`.
- `historical-data-acquisition-report` generated acquisition JSON and Markdown.
- `audit-historical-data-acquisition` passed with `overall_passed=True` and no blocking reasons.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Isolated replay artifacts were written under `data/replays/global_briefing/`.
- `run-daily` was not called.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.
- Forward dry-run was not started or validated.

Boundaries remain strict: historical data authorization is not trading authorization, proxy signals are not internal global-briefing signals, production global-briefing package status is separately reported, historical replay is not forward dry-run validation, historical replay is not strategy effectiveness proof, the system is not live trading ready, no broker/live/RL/LLM decision capability was added, and no real orders are supported.

Validation: 698 tests passed, 1 skipped.

## v0.5.6.1-warning-triage-evidence-quality

This patch release adds evidence-quality reporting around the v0.5.6 real-package-style global-briefing integration artifacts. It does not add replay functionality or trading functionality.

Includes:

- warning triage for v0.5.6 artifacts
- evidence quality report
- production global-briefing package acceptance criteria
- evidence quality audit
- explicit clarification that `GB-REAL-FIXTURE` is not a production package

Audited & Validated scope:

- `global-briefing-warning-triage` generated warning triage JSON and Markdown.
- `global-briefing-evidence-quality-report` generated evidence quality JSON and Markdown.
- `global-briefing-production-acceptance-criteria` generated machine-readable criteria, system Markdown, and docs Markdown.
- `audit-global-briefing-evidence-quality` passed with `overall_passed=True`.
- Blocking reasons: none.
- Production readiness remains `false`.
- Recommended production minimum coverage is `0.80`.
- Recommended production target coverage is `0.90`.
- Main orders/trades/portfolio/accounts ledgers were not written.
- `run-daily` was not called.
- No network request was used.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.
- Forward dry-run was not started or validated.

Boundaries remain strict: evidence-quality only, `GB-REAL-FIXTURE` is not a production package, production global-briefing historical coverage is not validated, strategy effectiveness is not proven, forward dry-run is not validated, live trading readiness is not certified, no broker, no real orders, no promotion, no RL trading, and no LLM trading decisions.

Validation: 669 tests passed, 1 skipped.

## v0.5.6-real-global-briefing-signal-integration-audited

This release adds the local real global-briefing historical signal package integration layer on top of the audited isolated replay adapter.

Includes:

- local global-briefing package manifest generation
- real package normalization to the v1 signal contract
- package coverage and point-in-time audit
- real package isolated replay workflow
- integration report
- real package integration release audit
- fixture-based local package inputs for JSONL/CSV and point-in-time checks

Audited & Validated scope:

- `global-briefing-package-manifest --root tests/fixtures/global_briefing_real` found local package files.
- `normalize-global-briefing-package` generated `data/global_briefing/normalized/GB-REAL-FIXTURE.normalized.jsonl`.
- `audit-global-briefing-package-coverage` passed with `coverage_ratio=0.6` and no blocking reasons.
- `run-global-briefing-real-package-replay --execution-mode isolated` completed with `overall_status=research_review_ready`.
- `global-briefing-real-package-report` produced `overall_status=research_review_ready`.
- `audit-global-briefing-real-package-integration` passed with `overall_passed=True`.
- Blocking reasons: none.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Only isolated replay ledger artifacts were written under `data/replays/global_briefing/`.
- `run-daily` was not called.
- No network request was used.
- Labels, ML shadow, experiments, promotion outputs, RL, and LLM trading decisions were not used.
- Forward dry-run was not started or validated.

Boundaries remain strict: local historical package integration only, not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, no broker, no real orders, no strategy state or parameter changes, no promotion, no RL trading, and no LLM trading decisions.

Validation: 633 tests passed, 1 skipped.

## v0.5.5-isolated-replay-execution-adapter-audited

This release adds the isolated replay execution adapter for global-briefing historical replay. The fixture E2E path no longer uses the no-trade fallback; it generates isolated virtual signals, orders, trades, portfolio, account, valuations, and summary artifacts under `data/replays/global_briefing/`.

Includes:

- isolated replay state model
- global-briefing signal-to-target adapter
- isolated order/execution/valuation adapter
- isolated replay ledger writer
- replay runner isolated execution mode
- replay evaluation upgrade
- isolated replay adapter audit

Audited & Validated scope:

- `replay-global-briefing-history --execution-mode isolated` generated isolated execution artifacts.
- `execution.mode=isolated`.
- `no_trade_fallback=false`.
- Isolated account, signals, orders, trades, portfolio, and valuations outputs exist.
- All isolated replay ledger outputs are under `data/replays/global_briefing/`.
- Main ledger not written.
- run-daily not called.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.
- `audit-isolated-replay-adapter` passed with `overall_passed=True`.
- Blocking reasons: none.

Boundaries remain strict: not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, no broker, no real orders, no strategy state or parameter changes, no RL trading, and no LLM trading decisions.

Validation: 572 tests passed, 1 skipped.

## v0.5.4-global-briefing-historical-replay-harness-audited

This release adds the full global-briefing historical replay harness. It establishes a repeatable, auditable, isolated replay framework for future historical macro signal packages.

Includes:

- global-briefing signal contract
- signal package validator
- point-in-time replay bundle
- isolated historical replay harness
- replay evaluation report
- replay audit
- fixture-based end-to-end smoke inputs for signal and price packages

Audited & Validated scope:

- `global-briefing-contract` generated contract JSON and Markdown.
- `validate-global-briefing-signals` passed on the fixture signal package.
- `build-global-briefing-replay-bundle` generated a point-in-time bundle with `future_signal_used=False`.
- `replay-global-briefing-history` generated an isolated no-trade replay summary.
- `global-briefing-replay-report` produced `overall_status=research_review_ready`.
- `audit-global-briefing-replay` passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- Main ledger not written.
- run-daily not called.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.

Boundaries remain strict: not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, no broker, no real orders, isolated replay only, no strategy state or parameter changes, no RL trading, and no LLM trading decisions.

Validation: 518 tests passed, 1 skipped.

## v0.5.3-forward-dry-run-readiness-audited

This release adds a readiness-only audit for preparing a future 30 trading-day virtual forward dry-run. It does not start or validate the forward dry-run.

Includes:

- forward dry-run readiness audit
- day-0 checklist
- 30 trading-day forward plan
- protected path snapshot
- run-daily isolation check
- future-data leakage readiness check
- artifact separation check
- readiness-only safety boundary report

Audited & Validated scope:

- `forward-dry-run-readiness --trading-days 30` generated JSON and Markdown.
- Day-0 checklist and 30 trading-day plan were generated.
- Readiness audit passed with `overall_passed=True`.
- Blocking reasons: none.
- Warning: trading calendar not found; manual calendar confirmation is required before day 1.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called by the readiness validation flow.

Boundaries remain strict: readiness-only, dry-run not started, dry-run not validated, no live trading, no broker, no real orders, no auto promotion, no strategy state or parameter changes, no main ledger writes, no RL trading, no LLM trading decisions, and no strategy effectiveness proof.

Validation: 435 tests passed, 1 skipped.

## v0.5.2-usability-polish

This release adds usability polish for finding reports, locating current artifacts, and resuming project work. It does not add trading functionality.

Includes:

- corrected final handoff wording
- report index
- latest artifact locator
- artifact browser
- quick status
- command cookbook
- usability audit

Audited & Validated scope:

- `final-handoff-review` regenerated with corrected pytest and candidate wording.
- `report-index --include-audit --include-experiments --include-system` generated JSON and Markdown.
- `latest-artifact --type handoff` and `latest-artifact --type all` generated locator output.
- `artifact-browser` generated JSON and Markdown.
- `quick-status` generated JSON and Markdown.
- `usability-audit` passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called by the usability validation flow.

Boundaries remain strict: no trading functionality added, no live trading, no broker integration, no real orders, no auto promotion, no strategy state or parameter changes, no RL trading, and no LLM trading decisions. Forward 30d dry-run is still not completed.

Validation: 410 tests passed, 1 skipped.

## v0.5.1-system-integrity-and-documentation

This release consolidates system integrity documentation and auditability without adding trading capability.

Includes:

- documentation consolidation across README and docs/
- CLI inventory
- artifact inventory
- system smoke test
- boundary regression audit
- system integrity audit

Audited & Validated scope:

- `cli-inventory` generated JSON and Markdown.
- `artifact-inventory` generated JSON and Markdown.
- `system-smoke-test --include-reports --include-inventory` passed.
- `boundary-regression-audit` passed.
- `system-integrity-audit` passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called by the system integrity validation flow.

Boundaries remain strict: no live trading, no broker integration, no real orders, no auto promotion, no strategy state or parameter changes, no RL trading, and no LLM trading decisions. Forward 30d dry-run is still not completed.

Validation: 374 tests passed, 1 skipped.

## v0.5.1-validation-gap-remediation

This patch release remediates selected v0.5 validation gaps without expanding the trading scope.

Includes:

- `project_timezone` changed from `Asia/Tokyo` to `Asia/Shanghai`.
- `max_daily_turnover` is now enforced by the risk engine.
- `mistake_pattern_library.json` now includes explicit diagnostic boundary metadata.
- v0.5.1 remediation JSON and Markdown audit artifacts.

Deferred gaps:

- Market-rule-aware execution remains deferred to v0.6.
- Generalized Point-in-Time schema remains deferred to v0.7.

Boundaries remain strict: no broker integration, no live trading, no active promotion, no strategy state or parameter changes, no main ledger writes, no RL trading, and no LLM trading decisions. The v0.5.0 tag was not moved.

Validation: 345 tests passed, 1 skipped.

## v0.5.0-research-reporting-control-plane-audited

This release adds the v0.5 research reporting and control plane.

Includes:

- weekly research report
- monthly research report
- system dashboard
- project status report
- one-command research reporting pipeline
- reporting system release audit

Audited & Validated scope:

- Weekly and monthly reports generated from existing artifacts.
- System dashboard and project status reports generated.
- Research pipeline generated all v0.5 reporting artifacts.
- Reporting system audit passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called or modified by the reporting pipeline.
- The reports remain research-only and do not validate forward 30d dry-run.

Boundaries remain strict: no broker integration, no live trading, no active promotion, no strategy state or parameter changes, no main ledger writes, no RL trading, and no LLM trading decisions.

Validation: 330 tests passed, 1 skipped.

## v0.3.0-ml-shadow-pipeline-audited

This release adds the ML shadow research pipeline v1 (audited).

Includes:

- feature store v1
- label versioning v1
- walk-forward dataset builder
- ML shadow model scaffold
- ML prediction output
- ML shadow signal generator
- ML shadow leaderboard
- ML shadow research report

Audited & Validated scope:

- Walk-forward dataset builder validated.
- ML shadow model training and inference scaffold verified.
- ML shadow prediction file output (predictions.jsonl) successfully written.
- ML shadow signal generator (ml_shadow_signals.jsonl) successfully generated.
- ML shadow leaderboard recommendation generated as "watch".
- ML shadow research report successfully compiled.
- Independent boundaries audited (no broker connections, no live-trading logic, no main ledger pollution).
- Data leakage: none (chronological split enforced).
- Audit verdict: PASS_WITH_NO_ACTION.

Boundaries remain strict: no broker integration, no live trading, no active ML signals execution, no active ledger pollution.

Validation: 188 tests passed.

## v0.2.1-price-only-historical-replay-validated

This release adds historical 30-trading-day price-only replay validation.

Validated scope:

- Historical 30-trading-day price-only replay passed.
- Replay date range: 2026-05-11 to 2026-06-22.
- `historical_replay_passed=True`.
- `price_only_replay=True`.
- `forward_30d_dry_run_passed=False`.
- No real macro_signals were available.
- Replay did not pollute main daily-run ledger.
- Critical errors: 0.

This release is not a full historical global-briefing replay and is not future 30-day forward dry-run validation. Boundaries remain strict: no broker integration, no live trading, no real orders, no ML, no RL, and no LLM trading decisions.

Validation: 144 tests passed.

## v0.2.0-historical-real-data-validated

This release marks Trading Core as a historical real-data validated, file-backed virtual trading research base.

Validated scope:

- Historical real ETF data validation passed.
- Batch backtest passed.
- Backtest consistency passed.
- Real-data validation report passed.
- `dry_run_30d_passed=False`.
- Blocking reason: `actual_run_days_below_30`, `missing_real_global_briefing_inputs`.

This release does not represent 30-day real global-briefing dry-run validation. Boundaries remain strict: no broker integration, no live trading, no real orders, no ML, no RL, and no LLM trading decisions.

Validation: 136 tests passed.

## v0.1.0-core-hardened

This release freezes the first hardened version of Trading Core as a file-backed virtual trading research base.

It supports daily dry-runs, runtime health files, ETF historical CSV import, strategy backtests, admission decisions, global-briefing summary export, and throttled evolution artifacts.

Boundaries remain strict: no broker integration, no live trading, no real orders, no ML, no RL, and no LLM trading decisions.

Freeze scope: Issue 1-36 complete.

Validation: 83 tests passed.
