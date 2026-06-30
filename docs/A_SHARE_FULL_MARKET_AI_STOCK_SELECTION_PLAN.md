# A Share Full Market AI Stock Selection Plan

## v0.8.6 ops history baseline note

v0.8.6 adds an operational run-history layer after the v0.8.5 daily ops command center. It records real ops runs, evaluates whether trend baselines have enough observations, and keeps health/module/warning/issue/action/boundary history indexes.

This phase does not produce trading recommendations, order previews, broker actions, or live-ready claims. With only the first real v0.8.5 ops run available, the release baseline correctly reports `run_history_observation_count=1` and `baseline_status=insufficient_history`.

## v0.8.7 gated current-day dry-run note

v0.8.7 executes the first gated current-day `build_from_existing_data` dry-run from existing local data and audited operations artifacts. It requires a preflight gate, records validate-vs-build comparison and artifact drift, and prepares v0.8.8 repeatability/diff-stability hardening.

This phase does not refresh public network data, does not run `full_research_run`, does not generate buy/sell signals, does not generate order previews, does not connect broker, does not place real orders, does not call old `run-daily`, and does not execute official forward dry-run day2.

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
  - implemented orchestration-only outputs: workflow config, preflight, stage manifest, run manifest, source trace, boundary check, owner summary, reports, and audit
  - result as of 2026-06-26: validate_existing_artifacts mode passed, 11/11 stages passed, source trace complete, upstream audits passed, workflow audit passed, recommended next version `v0.7.10-a-share-benchmark-data-and-performance-comparison`
  - boundary: no upstream module rewrite, no old run-daily, no official forward dry-run day2, no broker, no real orders, no buy/sell signals, no order preview, no profit claim, no live-trading readiness

- v0.7.10 benchmark data and performance comparison
  - implemented benchmark-only outputs: CSI300, CSI500, CSI1000, CASH, strict-tradable equal-weight, candidate-pool equal-weight, benchmark availability, price/return/NAV snapshots, portfolio comparison, relative performance, exclusion report, source trace, boundary check, reports, and audit
  - result as of 2026-06-26: all six benchmark ids available, placeholder benchmarks used none, first-day portfolio limitations explicit, benchmark audit passed, recommended next version `v0.7.11-a-share-multi-day-portfolio-performance-tracking`
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
- `src/trading_core/equity_workflows/`
- `src/trading_core/equity_benchmarks/`
- `src/trading_core/equity_validation/`
- `src/trading_core/integrations/`
- `data/equity_universe/`, `data/equity_market/`, `data/equity_industry/`, `data/equity_fundamental/`, `data/equity_data_quality/`, `data/equity_features/`, `data/equity_scores/`, `data/equity_selection/`, `data/equity_portfolios/`, `data/equity_briefings/`, `data/equity_portfolio_tracking/`, `data/equity_workflows/`, `data/equity_benchmarks/`, `data/equity_validation/`
- `outputs/equity_selection/`, `outputs/equity_scores/`, `outputs/equity_portfolios/`, `outputs/equity_briefings/`, `outputs/equity_portfolio_tracking/`, `outputs/equity_workflows/`, `outputs/equity_benchmarks/`, `outputs/equity_validation/`

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
- v0.7.9 workflow orchestration artifacts are research-only; they orchestrate v0.7.2-v0.7.8 stages and do not rewrite business modules, call old `run-daily`, execute day2, connect a broker, place real orders, generate buy/sell signals, generate order previews, claim profitability, or certify live readiness.
- v0.7.10 benchmark comparison artifacts are research-only; they compare virtual portfolios to benchmark series, keep limited first-day history explicit, and do not create buy/sell signals, generate order previews, connect a broker, place real orders, call old `run-daily`, execute day2, claim profitability, or certify live readiness.
- v0.7.12 attribution and risk diagnostics artifacts are research-only; they explain virtual portfolio structure and limited-history attribution status, and do not create buy/sell signals, generate order previews, connect a broker, place real orders, call old `run-daily`, execute day2, fabricate performance, claim profitability, or certify live readiness.

## v0.7.11 Performance Tracking Update

v0.7.11 adds multi-day virtual portfolio performance tracking to the A-share full-market research chain. It materializes NAV, daily return, cumulative return, drawdown, benchmark-relative status, holding mark-to-market, limitations, source trace, boundary check, and audit artifacts.

The release does not create buy/sell signals, does not place orders, does not connect a broker, does not call old `run-daily`, does not execute official forward dry-run day2, and does not fabricate portfolio history. The default 2026-06-26 release has one portfolio observation, so it explicitly distinguishes limited history from observed performance.

v0.7.12 adds attribution and risk diagnostics while preserving the limited-history boundary. It distinguishes structural diagnostics from realized performance attribution.

## v0.8.0 Daily Data Refresh Update

v0.8.0 adds daily data refresh and provider hardening. It validates schema, freshness, coverage, provider health, fallback decisions, source trace, and audit boundaries for A-share research data.

v0.8.0 does not generate buy/sell signals, does not place orders, does not connect broker, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat data freshness as trading readiness. v0.8.1 should use refreshed data to run the current-day research workflow.

## v0.8.1 Current-Day Research Runner Update

v0.8.1 adds a current-day research workflow runner after the data refresh layer. It requires the v0.8.0 data refresh audit to pass, runs the new A-share daily research workflow CLI for the resolved date, collects workflow and audit outputs, carries forward warnings, and writes owner-facing current-day run summaries.

v0.8.1 does not generate buy/sell signals, does not generate order previews, does not place orders, does not connect broker, does not read real account data, does not call old `run-daily`, does not execute official forward dry-run day2, and does not treat research output as trade instruction.

## v0.8.2 Owner Dashboard Update

v0.8.2 adds an owner-facing dashboard and monitoring package for the existing current-day run. It materializes executive status, data freshness, provider health, workflow status, research output, candidates, virtual portfolios, benchmarks, performance, attribution, warnings/blockers, navigation, source trace, boundary, manifest, summary, reports, and audit artifacts.

v0.8.2 does not refresh data, rerun the research workflow, generate buy/sell signals, generate order previews, place orders, connect broker, read real account data, call old `run-daily`, execute official forward dry-run day2, or treat dashboard content as trade instruction.

## v0.8.3 Owner Monitoring Update

v0.8.3 adds owner alerting and run history monitoring. It materializes monitoring config, input availability, append-only run history, warning/blocking/provider/workflow/dashboard trend snapshots, local alert rules, local alert evaluation, alert event log, monitoring cards, source trace, boundary, manifest, summary, reports, and audit artifacts.

v0.8.3 generates local alert artifacts only. It does not send external notifications by default, refresh data, rerun the research workflow, generate buy/sell signals, generate order previews, place orders, connect broker, read real account data, call old `run-daily`, execute official forward dry-run day2, or treat alerts as trade instructions. v0.8.4 should add owner remediation runbooks and safe action checklists.
# v0.8.4 Owner Remediation Runbook Alignment

v0.8.4 adds owner remediation runbook and safe action checklist material on top of the v0.8.3 monitoring layer.

- It generates plans and checklists only.
- It does not execute remediation actions.
- It does not refresh data.
- It does not rerun research workflow.
- It does not generate buy/sell signals.
- It does not place orders.
- It does not connect broker.
- It does not call old run-daily.
- It does not execute official forward dry-run day2.
- It does not treat remediation as trade instruction.
- v0.8.5 should add daily ops command center.
# v0.8.5 Daily Ops Command Center Alignment

v0.8.5 adds the A-share daily ops command center as an owner-facing operations control plane.

- v0.8.5 aggregates existing ops artifacts by default.
- v0.8.5 does not refresh data by default.
- v0.8.5 does not rerun current-day research by default.
- v0.8.5 does not execute remediation actions.
- v0.8.5 does not generate buy/sell signals.
- v0.8.5 does not place orders.
- v0.8.5 does not connect broker.
- v0.8.5 does not call old run-daily.
- v0.8.5 does not execute official forward dry-run day2.
- v0.8.5 does not treat ops output as trade instruction.
- v0.8.6 should deepen run history and trend baselines.
# v0.8.8 Build Repeatability Addendum

v0.8.8 adds A-share `build_from_existing_data` repeatability and diff stability. It repeats the gated v0.8.7 build for the same `as_of_date`, compares first-build and second-build artifacts, classifies timestamp-only drift, metadata/hash drift, business output drift, missing required artifacts, boundary drift, protected path drift, and source trace drift.

The stage distinguishes pre-existing protected paths from modified protected paths. Pre-existing `data/orders` or `data/trades` are not automatically blocking; new, modified, or deleted files under protected order/trade/account paths are blocking.

This stage does not refresh public network data, does not run `full_research_run`, does not generate buy/sell signals, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, and does not treat repeatability as a trade instruction. v0.8.9 should refresh owner dashboard outputs from `build_from_existing_data` artifacts.

## v0.8.9 Build-Output Owner Dashboard Addendum

v0.8.9 refreshes the owner dashboard from `build_from_existing_data` output. It prefers build output over validate-source artifacts, requires repeatability audit success, requires `business_output_drift_count=0`, and distinguishes pre-existing protected paths from modified protected paths.

This stage does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not generate buy/sell signals, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, and does not treat the dashboard as a trade instruction. v0.8.10 should refresh monitoring, remediation, ops center, and ops history from build output.

## v0.8.10 Build-Output Ops Refresh Addendum

v0.8.10 propagates v0.8.9 build-output dashboard state into monitoring, remediation, ops center, and ops history refresh artifacts. It keeps original monitoring/remediation/ops artifacts as comparison sources and uses `build_from_existing_data` as the source workflow mode.

This stage does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not generate buy/sell signals, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, and does not treat ops refresh as trade instruction. v0.8.11 should build the daily owner decision pack and runbook from the build-output ops refresh.

## v0.8.11 Owner Daily Pack Addendum

v0.8.11 builds an owner-facing daily runbook and owner operations decision pack from the v0.8.10 build-output ops refresh. It materializes input availability, source resolution, date alignment, status brief, runbook, operations decision pack, next-step checklist, research/candidate/virtual-portfolio/warning/safe-action/ops/protected-path/source/boundary digests, navigation, source trace, boundary check, manifest, summary, reports, and audit artifacts.

This stage is not an investment decision pack and is not a trading system. It does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not generate buy/sell signals, does not generate order previews, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, does not treat research candidates as recommendations, and does not treat the daily pack as a trade instruction. v0.8.12 should append daily packs to history and trend owner readiness, pack quality, warning recurrence, and operational readiness over time.

## v0.8.12 Owner Daily Pack History Addendum

v0.8.12 appends the v0.8.11 owner daily pack to append-only history and computes owner-readiness trend artifacts. It materializes the run record, append result, history snapshot, owner readiness score/history/sufficiency, daily pack quality baseline, warning/safe-action/protected-path/boundary/source/completeness/next-step trends, source trace, boundary, manifest, reports, and audit artifacts.

This stage uses only real available daily pack records. It does not fabricate historical daily packs, does not fabricate trends, does not rerun `build_from_existing_data`, does not rerun owner daily pack, does not refresh public network data, does not run `full_research_run`, does not execute remediation actions, does not send external notifications, does not generate buy/sell signals, does not generate order previews, does not place orders, does not connect broker, does not call old run-daily, does not execute official forward dry-run day2, and does not treat owner readiness as a trade instruction. v0.8.13 should add owner-readiness gates and daily pack quality thresholds.
## v0.8.13 Owner Readiness Gate

v0.8.13 adds owner-readiness gate and daily pack quality thresholds after owner daily pack history. The stage evaluates owner operations acceptability only. It does not rerun `build_from_existing_data`, rerun owner daily pack, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, place orders, connect broker, call old `run-daily`, execute official forward dry-run day2, or treat the owner-readiness gate as a trade instruction.

v0.8.14 should add quality exception records, escalation workflow, and owner follow-up tracking.

## v0.8.14 Owner Quality Exception Workflow

v0.8.14 adds daily pack quality exception and escalation workflow after the owner-readiness gate. It preserves blocked gate decisions, explains audit-passed-but-gate-blocked states, does not auto-waive quality gates, does not change the v0.8.13 gate decision, and does not treat quality exceptions as trade instructions.

v0.8.15 should add an owner readiness recovery plan and measurable quality improvement loop.
## v0.8.16 Owner-Readiness Recovery Execution

v0.8.16 adds recovery execution tracking and gate reevaluation preparation on top of the v0.8.15 recovery plan.

This stage tracks evidence but does not fabricate completion, rerun owner readiness gate, change blocked gate decision, lower readiness thresholds, auto-waive quality gates, rerun `build_from_existing_data`, rerun owner daily pack, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, place orders, connect broker, call old `run-daily`, execute official forward dry-run day2, or treat recovery execution as trade instruction.

v0.8.17 should perform controlled gate reevaluation only if evidence readiness is sufficient.

## v0.8.15 Owner-Readiness Recovery Plan

v0.8.15 adds a recovery plan and quality improvement loop for the owner-readiness blocked state produced by the v0.8.13 gate and v0.8.14 quality exception workflow.

This stage preserves blocked gate state, does not lower readiness thresholds, does not auto-waive quality gates, does not mark recovery tasks complete by default, and does not rerun upstream A-share build, gate, or daily pack workflows.

v0.8.16 should track recovery task evidence and prepare a controlled gate reevaluation without weakening thresholds.

## v0.8.17 Owner-Readiness Controlled Gate Reevaluation

v0.8.17 consumes the v0.8.16 recovery execution package and evaluates whether a gate reevaluation is allowed. The audited 2026-06-26 state is `skipped_not_ready` because recovery evidence remains insufficient.

This stage records a controlled skip decision, preserves the v0.8.13 blocked gate decision, keeps the owner-readiness threshold unchanged, and keeps waiver approval absent. It does not rerun owner readiness gate, rerun `build_from_existing_data`, rerun owner daily pack, refresh public network data, run `full_research_run`, execute remediation actions, send external notifications, generate buy/sell signals, create order previews, connect broker, place orders, call old `run-daily`, execute official forward dry-run day2, or treat controlled reevaluation as trade instruction.

Primary outputs:

- `data/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/`
- `outputs/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/`
- `data/equity_data_quality/a_share_owner_controlled_gate_reevaluation_audit.json`
- `outputs/audit/A_SHARE_OWNER_CONTROLLED_GATE_REEVALUATION_AUDIT.md`

Recommended next version: `v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts`.
