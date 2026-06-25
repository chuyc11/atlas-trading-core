# Baseline Strategy Reporting

Baseline strategy reports summarize deterministic research baselines. They do not authorize day 1, forward dry-run, promotion, broker connection, or live trading.

## Report Inputs

- `data/strategies/baseline_strategy_contract.json`
- `data/strategies/baseline_strategy_registry.json`
- `data/strategies/signals/baseline_signals-STRATEGY_ID-START-END.jsonl`
- `data/strategies/order_previews/order_preview-STRATEGY_ID-START-END.jsonl`
- `data/replays/strategies/STRATEGY_ID/replay-START-END.json`
- `data/strategies/benchmark_comparison/baseline_benchmark_comparison-START-END.json`

## Report Outputs

- `data/strategies/reports/baseline_strategy_report-STRATEGY_ID-START-END.json`
- `outputs/strategies/BASELINE_STRATEGY_REPORT-STRATEGY_ID-START-END.md`
- `data/strategies/baseline_strategy_pack_summary.json`
- `outputs/strategies/BASELINE_STRATEGY_PACK_SUMMARY.md`
- `data/system/baseline_strategy_pack_audit.json`
- `outputs/audit/BASELINE_STRATEGY_PACK_AUDIT.md`

## Required Non-Claims

Each report must state:

- This is not strategy effectiveness proof.
- This is not forward dry-run validation.
- This is not live trading readiness.
- This does not trigger promotion.
- This does not use ML/LLM/RL for trading decisions.

## Quality Checks

- all three strategy reports exist
- PIT constraints are present
- benchmark comparison is present
- execution summary is present
- rejected orders and cost summary are present
- preview rows remain preview-only
- no main ledger writes occur
- no run-daily call occurs

## Daily Report Packet

v0.6.1 daily report packets summarize one-day daily baseline signals, order previews, isolated execution previews, warnings, cost estimates, and operator checklist items under `data/daily_workflow/reports/` and `outputs/daily_workflow/`. They do not trigger promotion and do not validate forward dry-run.
