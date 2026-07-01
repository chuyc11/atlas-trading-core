# Trading Core

## What this project is

- file-backed virtual trading research system
- A-share full-market AI stock selection planning and virtual portfolio tracking research
- paper / virtual trading only
- research workflow for ETF strategies, ML shadow, experiments, and reports

## What this project is not

- not a broker integration
- not live trading
- not investment advice
- not an auto-trading system
- not an RL trading agent
- not an LLM trading decision system

## Current release

v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts

## Completed milestones

- v0.1 core hardened
- v0.2 historical real-data validation
- v0.2.1 price-only historical replay
- v0.3 ML shadow audited
- v0.4 strategy experiment audited
- v0.5 reporting control plane audited
- v0.5.1 system integrity and documentation
- v0.5.2 usability polish
- v0.5.3 forward dry-run readiness audited
- v0.5.4 global-briefing historical replay harness audited
- v0.5.5 isolated replay execution adapter audited
- v0.5.6 real global-briefing signal integration audited
- v0.5.6.1 warning triage and evidence quality audited
- v0.5.7 authorized full historical data acquisition audited
- v0.5.7.1 historical data gap closure audited
- v0.5.8 day-0 operational readiness audited
- v0.5.8.1 plan alignment and MVP gap audited
- v0.5.9 A-share execution rules hardened
- v0.6.0 baseline strategy pack audited
- v0.6.1 daily workflow binding audited
- v0.6.2 forward dry-run start authorization pack audited
- v0.6.2.1 owner manual confirmation materialized
- v0.6.3 forward dry-run day 1 executed and audited
- v0.6.3.1 forward dry-run day1 continuation artifacts
- v0.6.3.2 forward dry-run day1 owner report pack
- v0.7.0 external project intake and A-share full-market selection plan
- v0.7.1 A-share full-market data ingestion foundation
- v0.7.1.2 A-share historical data provider expansion
- v0.7.2 A-share tradable universe filter
- v0.7.3 A-share multi-horizon feature engineering
- v0.7.4 A-share long/mid/short scoring system
- v0.7.5 A-share candidate generation system
- v0.7.6 A-share virtual portfolio construction
- v0.7.7 A-share daily stock selection briefing
- v0.7.8 A-share virtual portfolio tracking and paper ledger
- v0.7.9 A-share daily workflow orchestration
- v0.7.10 A-share benchmark data and performance comparison
- v0.7.11 A-share multi-day virtual portfolio performance tracking
- v0.7.12 A-share performance attribution and risk diagnostics
- v0.8.0 A-share daily data refresh and provider hardening
- v0.8.1 A-share current-day research workflow runner
- v0.8.2 A-share owner briefing and monitoring dashboard
- v0.8.3 A-share owner alerting and run history monitoring
- v0.8.4 A-share owner remediation runbook and safe action checklist
- v0.8.5 A-share daily ops command center
- v0.8.6 A-share ops run history deepening and trend baselines
- v0.8.7 A-share gated current-day build-from-existing-data dry-run
- v0.8.8 A-share build_from_existing_data repeatability and diff stability
- v0.8.9 A-share current-day build output owner dashboard refresh
- v0.8.10 A-share build-output monitoring remediation and ops refresh
- v0.8.11 A-share owner daily runbook and owner operations decision pack
- v0.8.12 A-share owner daily pack history and owner-readiness trends
- v0.8.13 A-share owner-readiness gate and daily pack quality thresholds
- v0.8.14 A-share owner daily pack quality exceptions and escalation workflow
- v0.8.15 A-share owner-readiness recovery plan and quality improvement loop
- v0.8.16 A-share owner-readiness recovery execution tracker and gate reevaluation prep
- v0.8.17 A-share owner-readiness controlled gate reevaluation
- v0.8.18 A-share recovery evidence collection and readiness improvement artifacts

## v0.8.18 owner-readiness recovery evidence boundary

- adds recovery evidence collection and readiness improvement artifacts
- records recovery task, developer follow-up, owner follow-up, quality issue, warning mapping, completeness, gap, blocker, score-impact estimate, and next reevaluation prep artifacts
- preserves the source blocked gate decision and source readiness score
- does not fabricate evidence or task completion
- does not rerun owner readiness gate, `build_from_existing_data`, or owner daily pack
- does not generate a new gate score or a new gate decision
- does not lower readiness thresholds or auto-waive quality gates
- does not refresh public network data, run `full_research_run`, execute remediation actions, or send external notifications
- does not generate buy/sell signals, order previews, broker connection, real account reads, or real orders
- does not call old `run-daily` or execute official forward dry-run day2
- uses targeted pytest only for this small version; full pytest is deferred to v0.9.0 or big-version closeout
- recommended next version: `v0.8.19-a-share-owner-readiness-evidence-backed-gate-reevaluation-prep`

## v0.8.17 owner-readiness controlled gate reevaluation boundary

- adds a controlled reevaluation adapter that evaluates whether gate reevaluation may run
- default audited state for 2026-06-26 is `skipped_not_ready`
- preserves the v0.8.13 blocked owner-readiness gate decision
- records `readiness_guard_passed=false`, `reevaluation_allowed=false`, and `reevaluation_skipped=true`
- does not generate a new gate score or a new gate decision
- does not rerun owner readiness gate, `build_from_existing_data`, or owner daily pack
- does not lower readiness thresholds or record auto/manual waiver approval
- does not refresh public network data or run `full_research_run`
- does not execute remediation actions or send external notifications
- does not generate buy/sell signals, order preview, broker connection, real account read, or real orders
- does not call old `run-daily` or execute official forward dry-run day2
- recommended next version: `v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts`

## v0.8.16 owner-readiness recovery execution boundary

- adds recovery execution tracker and gate reevaluation preparation
- tracks evidence but does not fabricate completion
- does not rerun owner readiness gate
- does not change blocked gate decision
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data or run `full_research_run`
- does not execute remediation actions or send external notifications
- does not generate buy/sell signals, order preview, broker connection, real account read, or real orders
- does not call old `run-daily` or execute official forward dry-run day2
- does not treat recovery execution as trade instruction
- recommended next version: `v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation`

## v0.8.15 owner-readiness recovery boundary

- adds owner-readiness recovery plan and quality improvement loop artifacts
- preserves the v0.8.13 blocked gate decision
- does not lower owner-readiness thresholds
- does not auto-waive quality gates
- does not mark recovery tasks complete by default
- does not rerun `build_from_existing_data`, owner readiness gate, or owner daily pack
- does not refresh public network data or run `full_research_run`
- does not execute remediation actions or send external notifications
- does not generate buy/sell signals, order preview, broker connection, real account read, or real orders
- does not call old `run-daily` or execute official forward dry-run day2
- does not treat the recovery plan as trade instruction
- recommended next version: `v0.8.16-a-share-owner-readiness-recovery-execution-tracker-and-gate-reevaluation-prep`

## v0.8.12 owner daily pack history boundary

- adds append-only owner daily pack history and owner-readiness trend artifacts
- uses v0.8.11 owner daily pack artifacts as the primary source
- release audit passed for `as_of_date=2026-06-26`
- source workflow mode is `build_from_existing_data`
- daily pack history observation count is 1
- minimum required observations is 5
- trend analysis is unavailable and correctly marked `insufficient_history`
- owner readiness score is 54 with grade D for the real 2026-06-26 pack
- uses append-only history by default
- does not fabricate historical daily packs
- does not fabricate trends
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not rerun ops refresh
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not treat owner readiness as trade instruction
- does not claim profit guarantee or live trading readiness
- recommended next version: v0.8.13-a-share-owner-readiness-gate-and-daily-pack-quality-thresholds

## v0.8.11 owner daily pack boundary

- adds owner daily runbook and owner operations decision pack
- uses v0.8.10 build-output ops refresh as the primary source
- reads supporting v0.8.9 dashboard, v0.8.8 repeatability, v0.8.7 gated build, and v0.8.0 data-refresh evidence
- release audit passed for `as_of_date=2026-06-26`
- source workflow mode is `build_from_existing_data`
- not an investment decision pack
- not a trade instruction
- keeps `business_output_drift_count=0`
- keeps `protected_path_modifications_detected=false`
- keeps `automatic_action_count=0`
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not claim profit guarantee or live trading readiness
- recommended next version: v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends

## v0.8.10 build-output ops refresh boundary

- refreshes monitoring, remediation, ops center, and ops history from the v0.8.9 build-output dashboard
- uses `build_from_existing_data` as source workflow mode
- requires build-output dashboard, repeatability, gated build, original monitoring, original remediation, and original ops center audits to pass
- requires `business_output_drift_count=0`
- requires `protected_path_modifications_detected=false`
- release audit passed for `as_of_date=2026-06-26`
- keeps `automatic_action_count=0`
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not treat ops refresh as trade instruction
- does not claim profit guarantee or live trading readiness
- recommended next version: v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack

## v0.8.9 build output owner dashboard boundary

- refreshes owner-facing dashboard artifacts from stable `build_from_existing_data` output
- prefers build output over validate-source artifacts
- requires v0.8.8 repeatability audit success
- requires `business_output_drift_count=0`
- distinguishes pre-existing protected paths from modified protected paths
- release audit passed for `as_of_date=2026-06-26`
- produces build-output dashboard data, owner reports, source trace, manifest, summary, and audit artifacts
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not treat dashboard output as a trade instruction
- does not claim profit guarantee or live trading readiness
- recommended next version: v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh

## v0.8.8 build repeatability boundary

- repeats the gated `build_from_existing_data` current-day workflow
- compares first-build and second-build artifacts
- classifies timestamp-only drift, metadata/hash drift, business output drift, missing artifacts, boundary drift, protected path drift, and source trace drift
- distinguishes pre-existing protected paths from modified protected paths
- pre-existing `data/orders` and `data/trades` are informational if unchanged
- new, modified, or deleted protected order/trade/account files are blocking
- business output drift is blocking by default
- release audit passed for `as_of_date=2026-06-26`
- does not refresh public network data
- does not run `full_research_run`
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not treat repeatability as a trade instruction
- does not claim profit guarantee or live trading readiness
- recommended next version: v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh

## v0.8.7 gated build-from-existing-data boundary

- adds gated current-day build-from-existing-data dry-run adapter
- validates v0.8.6 ops history, v0.8.5 ops center, v0.8.1 current-day, and v0.8.0 data refresh evidence before execution
- executes the current-day workflow only in `build_from_existing_data` mode
- preflight gate passed for `as_of_date=2026-06-26`
- workflow audit passed after execution
- validate-vs-build comparison completed with no missing required artifacts
- source trace is complete and input-source hashes match
- does not run public network refresh
- does not run `full_research_run`
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not send external notifications
- does not treat build output as a trade instruction
- does not claim profit guarantee or live trading readiness
- recommended next version: v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability

## v0.8.6 ops history boundary

- adds append-only ops run history and trend baseline artifacts
- reads existing v0.8.5 daily ops command center artifacts
- current release has one real observation
- `trend_analysis_available=false`
- `baseline_status=insufficient_history`
- does not synthesize history
- does not refresh data
- does not rerun current-day research
- does not generate buy/sell signals
- does not generate order preview
- does not place orders
- does not connect broker
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat trend baselines as trade instructions
- recommended next version: v0.8.7-a-share-gated-current-day-build-from-existing-data-dry-run

## v0.8.5 daily ops boundary

- adds daily ops command center
- aggregates existing ops artifacts by default
- does not refresh data by default
- does not rerun current-day research by default
- does not execute remediation actions
- does not generate buy/sell signals
- does not place orders
- does not connect broker
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat ops output as trade instruction
- recommended next version: v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines

## v0.8.4 owner remediation boundary

- adds owner remediation runbook and safe action checklist
- generates plans and checklists only
- does not execute remediation actions
- does not refresh data
- does not rerun research workflow
- does not generate buy/sell signals
- does not place orders
- does not connect broker
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat remediation as trade instruction
- recommended next version: v0.8.5-a-share-daily-ops-command-center

## Known limitations

- forward dry-run has started with virtual isolated day 1 complete; full 30d dry-run not completed
- authorized historical data access is available, but historical data authorization is not trading authorization
- authorized production global-briefing historical signal package is separately reported and may be `not_configured`
- unified proxy signals are research proxy signals, not internal global-briefing signals
- EPU may be repaired from authorized/local/API/FRED-compatible sources or represented by a policy-uncertainty proxy when official source access is unavailable
- OECD CLI may be repaired from authorized/local/API sources or represented by an authorized macro-cycle proxy explicitly marked as not official OECD CLI
- historical replay is not forward dry-run validation
- plan alignment is an audit, not day 1 authorization
- v0.5.9 hardens virtual execution rules but does not start forward dry-run
- v0.6.0 adds a research-only baseline strategy pack and does not start forward dry-run
- v0.6.1 binds daily research workflow previews using local authorized historical daily snapshots
- v0.6.2 creates a start authorization pack only and does not start forward dry-run
- v0.6.2 keeps manual confirmation false, owner authorization false, day1_start_allowed=false, day1_prompt_eligible=false, and day1_prompt_generated=false by default
- v0.6.2.1 materializes owner manual confirmation: manual_confirmation_complete=true, forward_dry_run_start_authorized=true, day1_prompt_eligible=true, day1_prompt_generated=false, and day1_start_allowed=false
- v0.6.3 executes virtual isolated forward dry-run day 1 only; it writes the forward dry-run ledger, not the main ledger
- v0.6.3.1 only fills day1 continuation artifact gaps; it does not execute day2
- v0.6.3.2 generates an owner-facing day1 report pack only; it does not execute day2, does not call run-daily, does not download real-time data, and does not call external APIs
- v0.7.0 downloads and scans external research repositories for design intake only; it does not merge third-party trading code into the main flow
- v0.7.0 starts the A-share full-market selection planning line; it does not ingest A-share market data yet, does not score stocks yet, and does not create real orders
- v0.7.1 builds the A-share data foundation only; it does not score stocks, generate candidates, generate virtual portfolios, connect a broker, place real orders, call run-daily, or execute official forward dry-run day2
- v0.7.1 may call public historical/delayed data endpoints; this is data ingestion only, not real-time trading data and not broker access
- v0.7.1 records free-source limitations in coverage/schema audits; adjusted prices, industry classification, and financial fields may be partial or fallback-labeled
- v0.7.1.1 historical panel backfill workflow is implemented and fail-closed in the current environment; public historical providers did not satisfy the release gate of 3000 price-history symbols
- v0.7.1.1 is not released as a success tag; no scores, candidates, virtual portfolios, broker calls, real orders, run-daily, or day2 artifacts were generated
- v0.7.1.2 expands historical data provider coverage and passes the minimum historical coverage gate for v0.7.2 preparation, but it still does not score stocks, generate candidates, generate watchlists, generate virtual portfolios, connect a broker, place real orders, call run-daily, or execute official forward dry-run day2
- v0.7.2 builds the A-share strict/caution/excluded/unknown tradable universe buckets only; it does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, broker calls, real orders, run-daily output, or official forward dry-run day2 artifacts
- v0.7.3 builds strict-universe multi-horizon feature artifacts only; it does not generate scores, candidates, watchlists, virtual portfolios, broker calls, real orders, run-daily output, profit claims, or official forward dry-run day2 artifacts
- v0.7.3 fundamental feature coverage is partial by design because several valuation percentile fields remain nullable placeholders for a later data-quality/scoring stage
- v0.7.4 builds strict-universe scores, ranks, distributions, component breakdowns, reports, and an audit only; it does not generate candidates, watchlists, virtual portfolios, buy/sell signals, broker calls, real orders, run-daily output, profit claims, live-trading readiness, or official forward dry-run day2 artifacts
- v0.7.4 scores are relative research inputs consumed by v0.7.5 candidate generation, not recommendations and not trading instructions
- v0.7.5 generates research candidates and extended watch pools only; candidates are not investment advice, not buy/sell signals, not order instructions, not virtual portfolios, not a profit guarantee, and not live-trading readiness
- v0.7.5 feeds v0.7.6 virtual portfolio construction and v0.7.7 daily owner briefing
- v0.7.6 generates research-only virtual portfolios and virtual target weights only; virtual portfolios are not real portfolios, target weights are not order instructions, no broker is connected, no real orders are placed, and no profit guarantee or live-trading readiness is claimed
- v0.7.7 generates a daily Chinese stock selection research briefing from existing artifacts only; it does not regenerate scores, candidates, or virtual portfolios, and it does not generate buy/sell signals, order previews, broker artifacts, real orders, profit claims, or live-trading readiness
- v0.7.8 generates research-only virtual portfolio tracking and paper ledgers only; paper ledgers are not real-money ledgers, virtual holdings are not real holdings, virtual returns are not actual returns, no broker is connected, and no real orders are placed
- v0.7.9 orchestrates the A-share daily research workflow only; it does not rewrite upstream business modules, does not call old `run-daily`, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals, and does not generate order previews
- v0.7.10 adds CSI300, CSI500, CSI1000, CASH, strict-tradable equal-weight, and candidate-pool equal-weight benchmark comparison; it is research-only, does not create buy/sell signals, does not place orders, does not connect a broker, does not call old `run-daily`, does not execute official forward dry-run day2, and flags limited first-day portfolio history
- v0.7.11 adds appendable multi-day virtual portfolio performance tracking with NAV, returns, drawdown, benchmark-relative status, holding mark-to-market, limitations, source trace, boundary check, and audit artifacts; it does not create buy/sell signals, does not place orders, does not connect a broker, does not call old `run-daily`, does not execute official forward dry-run day2, does not fabricate portfolio history, and distinguishes limited history from observed performance
- v0.7.12 adds performance attribution and risk diagnostics for existing virtual portfolios; it distinguishes structural diagnostics from realized performance attribution, correctly flags limited history, and does not create buy/sell signals, does not place orders, does not connect a broker, does not call old `run-daily`, does not execute official forward dry-run day2, and does not fabricate performance
- v0.8.0 validates daily A-share research data freshness and provider readiness; it does not trigger the full research workflow by default, does not create buy/sell signals, does not generate order previews, does not connect a broker, does not place real orders, does not call old `run-daily`, and does not execute official forward dry-run day2
- v0.8.1 requires the data refresh audit to pass, then runs the new A-share daily research workflow CLI for the current research date; it does not create buy/sell signals, does not generate order previews, does not connect a broker, does not read real account data, does not place real orders, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat research output as trade instruction
- v0.8.2 builds an owner-facing dashboard from existing current-day artifacts only; it does not refresh data, does not rerun workflow, does not create buy/sell signals, does not generate order previews, does not connect a broker, does not read real account data, does not place real orders, and does not treat dashboard content as trade instruction
- v0.8.3 builds local owner alerting and run-history monitoring from existing dashboard/current-day/data-refresh artifacts only; it does not send external notifications by default, does not refresh data, does not rerun workflow, does not generate buy/sell signals, does not generate order previews, does not connect a broker, does not read real account data, does not place real orders, and does not treat alerts as trade instructions
- day2 is blocked by local data horizon insufficiency; the latest common local market/benchmark/risk-proxy date is 2026-06-25, which day1 already used
- strategy effectiveness not proven
- no live trading

## Quickstart

Install and verify:

```powershell
python -m trading_core.cli --help
python -m pytest
```

Run v0.7 external intake:

```powershell
python scripts/download_external_research_repos.py
python -m trading_core.cli external-project-intake
```

Run v0.7.1 A-share data foundation:

```powershell
python -m trading_core.cli equity-data-source-manifest
python -m trading_core.cli build-a-share-equity-master
python -m trading_core.cli build-a-share-trading-calendar
python -m trading_core.cli ingest-a-share-daily-prices
python -m trading_core.cli ingest-a-share-adjusted-prices
python -m trading_core.cli ingest-a-share-daily-basic
python -m trading_core.cli ingest-a-share-industry-classification
python -m trading_core.cli ingest-a-share-basic-financials
python -m trading_core.cli audit-a-share-data-coverage
python -m trading_core.cli audit-a-share-data-schema
```

Or run the same foundation chain in one command:

```powershell
python -m trading_core.cli build-a-share-data-foundation
```

Run v0.7.2 A-share tradable universe filter:

```powershell
python -m trading_core.cli build-a-share-tradable-universe --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-tradable-universe --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-tradable-universe --as-of-date 2026-06-26
```

The default downstream input is `strict_tradable_universe`. `caution_universe` is observation-only unless a future command explicitly allows it.

Run v0.7.3 A-share multi-horizon feature engineering:

```powershell
python -m trading_core.cli build-a-share-multi-horizon-features --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-multi-horizon-features --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-multi-horizon-features --as-of-date 2026-06-26
```

The v0.7.3 output is feature input for a future scoring stage. It is not a score table, recommendation list, candidate list, watchlist, virtual portfolio, order plan, broker instruction, or live-trading readiness claim.

Run v0.7.4 A-share long/mid/short scoring:

```powershell
python -m trading_core.cli build-a-share-scores --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-scores --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-scores --as-of-date 2026-06-26
```

The v0.7.4 output is a score table and score audit for the strict tradable universe. It is not a recommendation list, not a virtual portfolio, not a buy/sell signal, not an order plan, not broker integration, not a profit guarantee, and not live-trading readiness. Candidate generation is handled by v0.7.5 and virtual portfolio construction is handled by v0.7.6.

Run v0.7.5 A-share candidate generation:

```powershell
python -m trading_core.cli generate-a-share-candidates --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-candidates --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli generate-and-audit-a-share-candidates --as-of-date 2026-06-26
```

The v0.7.5 output is a research candidate package for long, mid, and short horizons plus an extended watch pool, multi-horizon candidates, risk-downgraded candidates, reports, manifest, and audit. Candidates are not investment advice, not buy/sell signals, not order instructions, not virtual portfolios, not broker integration, not a profit guarantee, and not live-trading readiness. Virtual portfolios are handled by v0.7.6. Daily owner briefing is handled by v0.7.7.

Run v0.7.6 A-share virtual portfolio construction:

```powershell
python -m trading_core.cli build-a-share-virtual-portfolios --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolios --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-virtual-portfolios --as-of-date 2026-06-26
```

The v0.7.6 output is a research-only virtual portfolio package for long, mid, and short horizons plus target weights, industry exposure, risk/liquidity summaries, reports, manifest, and audit. Virtual portfolios are not real portfolios. Virtual target weights are not order instructions, not broker order previews, not buy/sell signals, not real orders, not profit guarantees, and not live-trading readiness. Daily owner briefing is handled by v0.7.7.

Run v0.7.7 A-share daily stock selection briefing:

```powershell
python -m trading_core.cli build-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-daily-stock-selection-briefing --as-of-date 2026-06-26
```

The v0.7.7 output is a Chinese research briefing for the project owner. It summarizes existing long/mid/short candidates, multi-horizon candidates, risk-downgraded candidates, virtual portfolios, industry exposure, risk/liquidity status, and audit state. It does not regenerate scores, candidates, or virtual portfolios. It is not investment advice, not a buy/sell signal, not an order preview, not a broker instruction, not a real-account action, not a profit guarantee, and not live-trading readiness.

Run v0.7.8 A-share virtual portfolio tracking and paper ledger:

```powershell
python -m trading_core.cli build-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli build-and-audit-a-share-virtual-portfolio-tracking --as-of-date 2026-06-26
```

The v0.7.8 output is a research-only virtual tracking package for the existing long/mid/short virtual portfolios. It creates virtual paper ledgers, holdings snapshots, NAV, first-day return/drawdown snapshots, exposure summaries, benchmark placeholders, reports, manifest, source trace, and audit. The paper ledger is not a real-money ledger. Virtual holdings are not real holdings. Virtual returns are not actual returns. It does not generate buy/sell signals, order previews, broker artifacts, real orders, profit claims, live-trading readiness, `run-daily`, or official forward dry-run day2 artifacts.

Run v0.7.9 A-share daily workflow orchestration:

```powershell
python -m trading_core.cli preflight-a-share-daily-workflow --as-of-date 2026-06-26
python -m trading_core.cli run-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
python -m trading_core.cli audit-a-share-daily-research-workflow --as-of-date 2026-06-26
```

Equivalent one-command path:

```powershell
python -m trading_core.cli run-and-audit-a-share-daily-research-workflow --as-of-date 2026-06-26 --mode validate_existing_artifacts
```

The v0.7.9 output is an orchestration-only daily research workflow package. It validates or runs the existing A-share research stages in order, writes workflow config, preflight, stage manifest, run manifest, source trace, boundary check, owner summary, and audit artifacts, and fails closed if a critical stage fails. It does not rewrite upstream business modules, does not call old `run-daily`, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals, does not generate order previews, does not claim model profitability, and is not live-trading ready. Benchmark data and relative performance comparison are deferred to v0.7.10.

Run v0.7.10 A-share benchmark data and performance comparison:

```powershell
python -m trading_core.cli build-a-share-benchmark-comparison --as-of-date 2026-06-26
python -m trading_core.cli audit-a-share-benchmark-comparison --as-of-date 2026-06-26
```

Combined:

```powershell
python -m trading_core.cli build-and-audit-a-share-benchmark-comparison --as-of-date 2026-06-26
```

The v0.7.10 output is a research-only benchmark package. It resolves the prior CSI300/CSI500/CSI1000 placeholder warning when real/public index history is available, adds CASH and equal-weight universe benchmarks, writes benchmark NAV/return snapshots, compares long/mid/short virtual portfolios against each benchmark, and explicitly marks first-day portfolio history as limited. It does not generate buy/sell signals, does not generate order previews, does not connect a broker, does not place real orders, does not call old `run-daily`, does not execute official forward dry-run day2, does not claim profitability, and is not live-trading ready.

Run v0.8.0 A-share daily data refresh and provider hardening:

```powershell
python -m trading_core.cli build-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data
python -m trading_core.cli audit-a-share-daily-data-refresh --as-of-date 2026-06-26
```

Combined:

```powershell
python -m trading_core.cli build-and-audit-a-share-daily-data-refresh --as-of-date 2026-06-26 --mode validate_existing_data
```

The v0.8.0 output is a data-refresh and provider-hardening package. It validates the latest usable research datasets, records provider registry/health/execution state, checks schema/freshness/coverage, reports data gaps and fallback choices, writes source trace and audit artifacts, and fails closed on critical data blockers. It does not trigger the full research workflow by default, does not generate buy/sell signals, does not generate order previews, does not connect a broker, does not place real orders, does not call old `run-daily`, does not execute official forward dry-run day2, does not claim profitability, and is not live-trading ready.

Run v0.8.1 A-share current-day research workflow runner:

```powershell
python -m trading_core.cli validate-a-share-current-day-readiness --as-of-date 2026-06-26
python -m trading_core.cli run-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
python -m trading_core.cli audit-a-share-current-day-research-run --as-of-date 2026-06-26
```

Combined:

```powershell
python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
```

The v0.8.1 output is a current-day research run package. It requires the v0.8.0 data refresh audit to pass, runs the new A-share daily research workflow CLI, collects workflow audit status and warnings, writes source trace, boundary, manifest, owner summary, and audit artifacts, and fails closed on readiness or workflow blockers. It does not generate buy/sell signals, does not generate order previews, does not connect a broker, does not read real account data, does not place real orders, does not call old `run-daily`, does not execute official forward dry-run day2, does not claim profitability, and is not live-trading ready.

Run v0.8.2 owner dashboard from an existing current-day run:

```powershell
python -m trading_core.cli validate-a-share-owner-dashboard-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
python -m trading_core.cli audit-a-share-owner-dashboard --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-owner-dashboard --as-of-date 2026-06-26 --mode build_dashboard_from_existing_run
```

The v0.8.2 output is an owner-facing monitoring package. It reads existing data refresh, workflow, briefing, tracking, benchmark, performance, attribution, and current-day run artifacts; it does not refresh data, rerun workflow, create trading instructions, connect a broker, or place orders.

Run v0.8.3 owner alerting and run-history monitoring:

```powershell
python -m trading_core.cli validate-a-share-owner-monitoring-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
python -m trading_core.cli audit-a-share-owner-monitoring --as-of-date 2026-06-26
python -m trading_core.cli build-and-audit-a-share-owner-monitoring --as-of-date 2026-06-26 --mode build_monitoring_dashboard
```

The v0.8.3 output is a local owner monitoring package. It writes alert and run-history artifacts only, does not send external notifications by default, does not refresh data, does not rerun workflow, does not connect a broker, does not place orders, and does not treat alerts as trading instructions.

The v0.7.1 foundation writes local data artifacts under `data/equity_universe/`, `data/equity_market/`, `data/equity_industry/`, `data/equity_fundamental/`, and `data/equity_data_quality/`. It does not write scores, candidates, virtual portfolios, broker artifacts, real orders, main ledgers, or official forward dry-run day2 artifacts.

Run v0.7.1.2 historical provider expansion and readiness checks:

```powershell
python -m trading_core.cli a-share-historical-backfill-plan
python -m trading_core.cli diagnose-a-share-historical-backfill-coverage
python -m trading_core.cli build-a-share-historical-backfill-symbol-queue
python -m trading_core.cli backfill-a-share-historical-panels-full-market --target-start-date 2021-01-01 --minimum-start-date 2023-01-01 --end-date 2026-06-26 --batch-size 100 --max-symbols 0 --resume --retry 2
python -m trading_core.cli audit-a-share-historical-panel-coverage
python -m trading_core.cli audit-a-share-feature-readiness
```

The v0.7.1.2 evidence resolves the v0.7.1.1 coverage blocker with 5516 price-history symbols, 1326 trading days, and passing coverage/readiness audits. This remains historical data preparation only; it is not scoring, candidate generation, portfolio generation, broker integration, or live trading readiness.

Run plan alignment and MVP gap audit:

```powershell
python -m trading_core.cli plan-checklist
python -m trading_core.cli mvp-requirement-map
python -m trading_core.cli artifact-coverage-scanner
python -m trading_core.cli classify-mvp-gaps
python -m trading_core.cli classify-day1-blockers
python -m trading_core.cli next-work-register
python -m trading_core.cli audit-plan-alignment
```

Run A-share execution rules hardening audit:

```powershell
python -m trading_core.cli ashare-execution-gap-plan
python -m trading_core.cli ashare-trading-calendar-audit
python -m trading_core.cli execution-timeline-contract
python -m trading_core.cli ashare-price-status-contract
python -m trading_core.cli ashare-lot-and-position-contract
python -m trading_core.cli ashare-execution-cost-contract
python -m trading_core.cli virtual-execution-contract
python -m trading_core.cli audit-isolated-ledger-invariants
python -m trading_core.cli execution-aware-replay-smoke
python -m trading_core.cli reclassify-day1-blockers-after-execution-hardening
python -m trading_core.cli audit-ashare-execution-rules
```

Run v0.6.0 baseline strategy pack:

```powershell
python -m trading_core.cli baseline-strategy-scope-plan
python -m trading_core.cli baseline-strategy-contract
python -m trading_core.cli baseline-strategy-registry
python -m trading_core.cli generate-baseline-strategy-signals --strategy all --start-date 2024-01-02 --end-date 2024-12-31
python -m trading_core.cli build-baseline-order-preview --strategy all --execution-mode isolated
python -m trading_core.cli replay-baseline-strategy --strategy all --start-date 2024-01-02 --end-date 2024-12-31 --execution-mode isolated
python -m trading_core.cli compare-baseline-strategy-benchmarks --strategy all --start-date 2024-01-02 --end-date 2024-12-31
python -m trading_core.cli baseline-strategy-report --strategy all --start-date 2024-01-02 --end-date 2024-12-31
python -m trading_core.cli baseline-strategy-pack-summary
python -m trading_core.cli audit-baseline-strategy-pack
python -m trading_core.cli reclassify-day1-blockers-after-baseline-strategies
```

Run v0.6.1 daily workflow binding:

```powershell
python -m trading_core.cli daily-workflow-scope-plan
python -m trading_core.cli daily-market-data-snapshot --as-of-date 2024-12-31
python -m trading_core.cli audit-daily-data-quality --snapshot data/daily_workflow/snapshots/daily_market_data_snapshot-2024-12-31.json
python -m trading_core.cli daily-input-freeze-manifest --as-of-date 2024-12-31
python -m trading_core.cli daily-baseline-signals --as-of-date 2024-12-31 --strategy all
python -m trading_core.cli daily-order-preview --as-of-date 2024-12-31 --strategy all --execution-mode isolated
python -m trading_core.cli daily-isolated-execution-preview --as-of-date 2024-12-31 --execution-mode isolated
python -m trading_core.cli daily-report-packet --as-of-date 2024-12-31
python -m trading_core.cli protected-path-residue-scan
python -m trading_core.cli audit-daily-workflow --as-of-date 2024-12-31
python -m trading_core.cli reclassify-day1-blockers-after-daily-workflow
```

Run v0.6.2 forward dry-run start authorization pack:

```powershell
python -m trading_core.cli forward-dry-run-authorization-scope-plan
python -m trading_core.cli forward-dry-run-start-prerequisite-inventory
python -m trading_core.cli current-daily-workflow-readiness-snapshot
python -m trading_core.cli forward-dry-run-manual-confirmation-checklist-v2
python -m trading_core.cli forward-dry-run-owner-authorization-packet
python -m trading_core.cli validate-forward-dry-run-start-gate-v062
python -m trading_core.cli forward-dry-run-run-daily-command-preview
python -m trading_core.cli forward-dry-run-day1-prompt-eligibility
python -m trading_core.cli audit-forward-dry-run-start-authorization
python -m trading_core.cli reclassify-day1-blockers-after-start-authorization
```

The v0.6.2 pack is fail-closed. Technical prerequisites are present, authorization remains pending, and the next required action is owner manual confirmation. The run-daily command preview is metadata only; run-daily is not called, forward dry-run is not started, the main ledger is not written, no broker is connected, ML/LLM/RL trading decisions are not added, and promotion is not triggered.

Run v0.6.2.1 owner manual confirmation materialization:

```powershell
python -m trading_core.cli forward-dry-run-owner-manual-confirmation-record
python -m trading_core.cli complete-forward-dry-run-manual-confirmation-checklist-v2
python -m trading_core.cli update-forward-dry-run-owner-authorization-packet
python -m trading_core.cli revalidate-forward-dry-run-start-gate-v0621
python -m trading_core.cli revalidate-forward-dry-run-day1-prompt-eligibility
python -m trading_core.cli audit-forward-dry-run-authorization-materialization
python -m trading_core.cli reclassify-day1-blockers-after-authorization-materialization
```

The v0.6.2.1 pack materializes owner manual confirmation but does not start forward dry-run day 1. The next required action is owner requests day1 prompt. It does not call run-daily, does not write the main ledger, does not validate forward dry-run, does not prove strategy effectiveness, and does not certify live trading readiness.

Run v0.6.3 virtual isolated forward dry-run day 1:

```powershell
python -m trading_core.cli forward-dry-run-day1-pre-execution-gate
python -m trading_core.cli forward-dry-run-day1-input-snapshot
python -m trading_core.cli forward-dry-run-day1-strategy-signals
python -m trading_core.cli forward-dry-run-day1-virtual-order-preview
python -m trading_core.cli forward-dry-run-day1-virtual-execution
python -m trading_core.cli forward-dry-run-day1-ledger-snapshot
python -m trading_core.cli forward-dry-run-day1-risk-boundary-report
python -m trading_core.cli forward-dry-run-day1-operator-report
python -m trading_core.cli audit-forward-dry-run-day1
python -m trading_core.cli forward-dry-run-status
python -m trading_core.cli reclassify-day1-blockers-after-forward-dry-run-day1
```

The v0.6.3 workflow executes day 1 in `forward_dry_run_virtual` mode using local authorized historical data as of 2026-06-25. It writes only isolated forward dry-run day 1 and ledger artifacts under `data/forward_dry_run/` and `outputs/forward_dry_run/`, plus status/audit summaries. It does not call run-daily, does not connect a broker, does not place real orders, does not write the main ledger, does not validate the full 30-day forward dry-run, does not prove strategy effectiveness, and does not certify live trading readiness.

Run v0.6.3.1 day1 continuation artifact materialization:

```powershell
python -m trading_core.cli forward-dry-run-day1-continuation-gap-analysis
python -m trading_core.cli forward-dry-run-day1-artifact-manifest
python -m trading_core.cli forward-dry-run-day1-reproducibility-manifest
python -m trading_core.cli forward-dry-run-day2-readiness-packet
python -m trading_core.cli forward-dry-run-day2-continuation-gate-preview
python -m trading_core.cli audit-forward-dry-run-day1-continuation-artifacts
python -m trading_core.cli reclassify-day1-continuation-artifacts-v0631
```

The v0.6.3.1 workflow absorbs the v0.6.4 blocking preflight and fills the missing day1 continuation artifacts required before a future day2 attempt. It does not execute day2 or day3, does not call run-daily, does not write the main ledger, and remains not strategy effectiveness proof, not full forward dry-run validation, and not live trading readiness.

Build features and labels:

```powershell
python -m trading_core.cli build-features --start-date 2024-01-01 --end-date 2026-06-23 --data data/raw/prices/etf_daily
python -m trading_core.cli build-labels --start-date 2024-01-01 --end-date 2026-06-23 --data data/raw/prices/etf_daily
```

Run ML shadow pipeline:

```powershell
python -m trading_core.cli build-ml-dataset --features data/features/features.jsonl --labels data/labels/labels.jsonl --start-date 2024-01-01 --end-date 2026-06-23 --train-days 252 --validation-days 63 --test-days 21 --step-days 21 --label-column forward_return_5d
python -m trading_core.cli train-ml-shadow --dataset data/ml/walk_forward_dataset.json --rows data/ml/walk_forward_rows.jsonl --model-type mock --label-column forward_return_5d
python -m trading_core.cli predict-ml-shadow --model data/ml/ml_shadow_model.json --rows data/ml/walk_forward_rows.jsonl
python -m trading_core.cli generate-ml-shadow-signals --predictions data/ml/ml_shadow_predictions.jsonl --top-k 3 --target-weight 0.05
python -m trading_core.cli ml-shadow-leaderboard --predictions data/ml/ml_shadow_predictions.jsonl --signals data/shadow/ml_shadow_signals.jsonl
```

Run experiment pipeline:

```powershell
python -m trading_core.cli register-experiment --config config/experiments/momentum_sweep.yaml
python -m trading_core.cli run-parameter-sweep --config config/experiments/momentum_sweep.yaml
python -m trading_core.cli compare-strategies --inputs data/experiments/parameter_sweep-EXP-sweep-momentum-20260624.json data/shadow/ml_shadow_leaderboard-2024-01-01-2026-06-23-MLSHADOW-20240101-20260623-mock.json
python -m trading_core.cli experiment-dashboard
```

Run reporting pipeline:

```powershell
python -m trading_core.cli weekly-research-report --start-date 2026-06-17 --end-date 2026-06-23 --include-experiments --include-ml-shadow --include-mistakes
python -m trading_core.cli monthly-research-report --start-date 2026-06-01 --end-date 2026-06-30 --include-weekly --include-experiments --include-ml-shadow
python -m trading_core.cli run-research-pipeline --start-date 2026-06-01 --end-date 2026-06-30
```

Run audits and system checks:

```powershell
python -m trading_core.cli cli-inventory
python -m trading_core.cli artifact-inventory
python -m trading_core.cli system-smoke-test --include-reports --include-inventory
python -m trading_core.cli boundary-regression-audit
python -m trading_core.cli system-integrity-audit
python -m trading_core.cli audit-global-briefing-replay
python -m trading_core.cli audit-isolated-replay-adapter
python -m trading_core.cli audit-global-briefing-real-package-integration
```

Run the global-briefing historical replay harness smoke:

```powershell
python -m trading_core.cli global-briefing-contract
python -m trading_core.cli validate-global-briefing-signals --input tests/fixtures/global_briefing/signals_valid.jsonl --start-date 2024-01-02 --end-date 2024-01-08
python -m trading_core.cli build-global-briefing-replay-bundle --signals tests/fixtures/global_briefing/signals_valid.jsonl --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --allow-carry-forward
python -m trading_core.cli replay-global-briefing-history --bundle data/replays/global_briefing/replay_bundle-2024-01-02-2024-01-08.json --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --execution-mode isolated --initial-cash 1000000
python -m trading_core.cli global-briefing-replay-report --replay data/replays/global_briefing/global_briefing_replay-2024-01-02-2024-01-08.json
python -m trading_core.cli audit-isolated-replay-adapter
```

Run the real global-briefing package integration smoke:

```powershell
python -m trading_core.cli global-briefing-package-manifest --root tests/fixtures/global_briefing_real
python -m trading_core.cli normalize-global-briefing-package --input tests/fixtures/global_briefing_real/real_package_aliases.csv --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1
python -m trading_core.cli audit-global-briefing-package-coverage --signals data/global_briefing/normalized/GB-REAL-FIXTURE.normalized.jsonl --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --min-coverage 0.60
python -m trading_core.cli run-global-briefing-real-package-replay --input tests/fixtures/global_briefing_real/real_package_aliases.csv --prices tests/fixtures/global_briefing_real/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --package-id GB-REAL-FIXTURE --region CN --source global_briefing --version v1 --allow-carry-forward --min-coverage 0.60 --execution-mode isolated
python -m trading_core.cli global-briefing-real-package-report
python -m trading_core.cli audit-global-briefing-real-package-integration
```

Run the global-briefing evidence quality reports:

```powershell
python -m trading_core.cli global-briefing-warning-triage
python -m trading_core.cli global-briefing-evidence-quality-report
python -m trading_core.cli global-briefing-production-acceptance-criteria
python -m trading_core.cli audit-global-briefing-evidence-quality
```

Run authorized full historical data acquisition and proxy replay:

```powershell
python -m trading_core.cli download-historical-data-packages --start-date 2018-01-01 --end-date latest --continue-on-error
python -m trading_core.cli normalize-historical-data-packages
python -m trading_core.cli audit-historical-data-quality
python -m trading_core.cli run-full-historical-proxy-replay --start-date 2024-01-02 --end-date 2024-12-31 --execution-mode isolated --min-coverage 0.80
python -m trading_core.cli historical-data-acquisition-report
python -m trading_core.cli audit-historical-data-acquisition
```

Run v0.5.7.1 historical data gap closure and warning reduction:

```powershell
python -m trading_core.cli close-historical-data-gaps --start-date 2018-01-01 --end-date latest --replay-start-date 2024-01-02 --replay-end-date 2024-12-31 --min-coverage 0.80 --continue-on-error
python -m trading_core.cli historical-data-gap-closure-report
python -m trading_core.cli audit-historical-data-gap-closure
```

Run v0.5.8 day-0 operational readiness pack:

```powershell
python -m trading_core.cli day0-data-freeze
python -m trading_core.cli day0-warning-register
python -m trading_core.cli day0-blocking-conditions
python -m trading_core.cli day0-run-daily-preflight
python -m trading_core.cli day0-manual-confirmation-packet
python -m trading_core.cli forward-dry-run-operating-calendar
python -m trading_core.cli day0-readiness-report
python -m trading_core.cli audit-day0-readiness
```

## Safety boundary

- no broker
- no live trading
- no real orders
- no auto promotion
- historical data authorization is not trading authorization
- authorized historical data acquisition does not connect to a broker and does not download account/order/trade/position/margin data
- local global-briefing package integration uses local files only and no network access
- v0.5.7 historical package acquisition may use approved public data endpoints and authorized local/API configuration for historical research data only
- v0.5.7.1 historical gap closure only repairs or proxies historical research packages and groups warnings
- v0.5.8 day-0 readiness does not start forward dry-run and does not call run-daily
- no forward dry-run started by the historical replay harness
- no forward dry-run started by the real package integration workflow
- no forward dry-run started by authorized historical data acquisition
- no labels, ML shadow, experiments, RL, or LLM trading decisions in the global-briefing replay decision path
- isolated replay ledger is written only under `data/replays/global_briefing/`
- v0.6.0 baseline strategy pack is research-only and does not start forward dry-run
- v0.6.0 isolated strategy replay ledgers are written only under `data/replays/strategies/`
- v0.6.1 daily workflow binding uses local authorized historical daily data snapshots and does not download real-time market data
- v0.6.1 writes preview artifacts only under `data/daily_workflow/` and `outputs/daily_workflow/`
- v0.7.1 writes A-share data foundation artifacts only under equity data/data-quality paths and does not call `run-daily`
- v0.7.5 writes A-share candidate and watch-pool artifacts only under equity selection paths; it does not generate virtual portfolios, buy/sell signals, order previews, broker calls, real orders, `run-daily`, profit claims, live-trading readiness, or official forward dry-run day2 artifacts
- v0.7.6 writes A-share virtual portfolio artifacts only under equity portfolio paths; it does not generate real portfolios, buy/sell signals, broker order previews, real orders, `run-daily`, profit claims, live-trading readiness, or official forward dry-run day2 artifacts
- v0.7.7 writes A-share daily briefing artifacts only under equity briefing paths; it reads existing artifacts only and does not regenerate scores, candidates, virtual portfolios, buy/sell signals, order previews, broker artifacts, real orders, `run-daily`, profit claims, live-trading readiness, or official forward dry-run day2 artifacts
- v0.7.8 writes A-share virtual tracking artifacts only under equity portfolio tracking paths and its audit under equity data quality/audit paths; it does not write main orders/trades/accounts, does not generate real portfolios, buy/sell signals, order previews, broker artifacts, real orders, `run-daily`, profit claims, live-trading readiness, or official forward dry-run day2 artifacts
- v0.7.9 writes A-share workflow orchestration artifacts only under `data/equity_workflows/`, `outputs/equity_workflows/`, and workflow audit paths; it does not rewrite upstream modules, does not call old `run-daily`, does not execute official forward dry-run day2, does not connect a broker, does not place real orders, does not generate buy/sell signals, does not generate order previews, and does not certify live-trading readiness
- v0.7.10 writes benchmark comparison artifacts only under `data/equity_benchmarks/`, `outputs/equity_benchmarks/`, and benchmark audit paths; it does not write main orders/trades/accounts, does not create buy/sell signals, does not generate order previews, does not connect a broker, does not place real orders, does not call old `run-daily`, and does not execute official forward dry-run day2
- v0.7.11 writes virtual performance tracking artifacts only under `data/equity_performance/`, `outputs/equity_performance/`, and audit paths; it does not fabricate history, connect a broker, place real orders, generate buy/sell signals, generate order previews, call old `run-daily`, or execute official forward dry-run day2
- v0.7.12 writes attribution and risk diagnostics only under `data/equity_attribution/`, `outputs/equity_attribution/`, and audit paths; it does not fabricate performance, connect a broker, place real orders, generate buy/sell signals, generate order previews, call old `run-daily`, or execute official forward dry-run day2
- v0.8.0 writes daily data refresh and provider hardening artifacts only under `data/equity_data_refresh/`, `outputs/equity_data_refresh/`, and audit paths; it does not trigger the full research workflow by default, does not connect a broker, does not place real orders, does not generate buy/sell signals, does not generate order previews, does not call old `run-daily`, and does not execute official forward dry-run day2
- v0.8.1 writes current-day research run artifacts only under `data/equity_current_day_runs/`, `outputs/equity_current_day_runs/`, and audit paths; it requires the data refresh audit first, does not connect a broker, does not read real account data, does not place real orders, does not generate buy/sell signals, does not generate order previews, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat research output as trade instruction
- v0.8.11 writes owner daily pack artifacts only under `data/equity_owner_daily_pack/`, `outputs/equity_owner_daily_pack/`, and audit paths; it uses build-output ops refresh as primary source, does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not connect a broker, does not place real orders, does not generate buy/sell signals, does not generate order previews, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat the pack as a trade instruction
- v0.8.12 writes owner daily pack history and readiness trend artifacts only under `data/equity_owner_daily_pack_history/`, `outputs/equity_owner_daily_pack_history/`, and audit paths; it uses append-only history, does not fabricate daily pack history, does not rerun `build_from_existing_data`, does not rerun owner daily pack, does not refresh public network data, does not run `full_research_run`, does not connect broker, does not place real orders, does not generate buy/sell signals or order previews, and does not treat owner readiness as a trade instruction
- v0.8.13 writes owner-readiness gate and daily pack quality threshold artifacts only under `data/equity_owner_readiness_gate/`, `outputs/equity_owner_readiness_gate/`, and audit paths; it evaluates owner operations acceptability only, may correctly block a pack whose readiness score is below threshold, does not rerun `build_from_existing_data`, does not rerun owner daily pack, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not connect broker, does not place real orders, does not generate buy/sell signals or order previews, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat the owner-readiness gate as a trade instruction
- v0.8.14 writes owner daily pack quality exception and escalation workflow artifacts only under `data/equity_owner_quality_exceptions/`, `outputs/equity_owner_quality_exceptions/`, and audit paths; it preserves blocked gate decisions, explains audit-passed-but-gate-blocked states, does not auto-waive quality gates, does not change the v0.8.13 gate decision, does not rerun `build_from_existing_data`, does not rerun owner readiness gate, does not rerun owner daily pack, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not generate buy/sell signals or order previews, does not connect broker, does not place real orders, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat quality exceptions as trade instruction
