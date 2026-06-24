# Release Notes

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
