# Release Notes

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
