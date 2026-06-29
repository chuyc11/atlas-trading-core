# A-Share Current-Day Run Audit

Audit command:

```bash
python -m trading_core.cli audit-a-share-current-day-research-run --as-of-date 2026-06-26
```

Combined release command:

```bash
python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
```

The audit verifies:

- current-day run artifacts exist
- data refresh audit passed
- data refresh blocking reasons are empty
- critical datasets passed
- schema, freshness, and coverage validation passed
- resolved date matches requested date unless explicitly waived
- workflow command does not call old run-daily
- workflow audit passed
- all current-day stages are present
- source trace is complete
- known warnings are carried forward
- boundary fields remain clean
- no broker, account, order, buy/sell signal, order preview, day2, or live-trading-ready state is generated

This audit is a research-run gate, not a trading-readiness gate.

