# Release Notes

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
