# A-Share Daily Pack History Audit

Run:

```bash
python -m trading_core.cli audit-a-share-owner-daily-pack-history --as-of-date 2026-06-26
```

The audit checks:

- all daily JSON artifacts exist
- all history indexes exist
- all Markdown reports exist
- v0.8.11 owner daily pack audit passed
- append-only rules are respected
- duplicate handling is recorded
- insufficient history is correctly flagged
- synthetic history is false
- future dates are false
- owner readiness score is valid
- no fabricated trends
- safe-action trends have no trade-like actions
- protected path trend is clean
- boundary trend is clean
- source trace is complete and hashes match
- no forbidden artifacts or positive trading wording are present

Audit mode does not append history, rebuild trends, rerun daily pack, rerun `build_from_existing_data`, refresh data, execute remediation, send notifications, connect broker, place orders, or create signals.
