# A-Share Ops History Audit

The audit command is:

```bash
python -m trading_core.cli audit-a-share-ops-history-baseline --as-of-date 2026-06-26
```

The audit checks:

- all required daily JSON, history indexes, and Markdown reports exist
- every artifact uses the v0.8.6 target version
- the v0.8.5 ops center audit passed and recommended v0.8.6
- append-only history completed
- observation count matches the history index
- insufficient history is correctly flagged when fewer than five real observations exist
- synthetic history and future dates are false
- source trace hashes match
- boundary flags remain clean

The audit output is written to `data/equity_data_quality/a_share_ops_history_baseline_audit.json` and `outputs/audit/A_SHARE_OPS_HISTORY_BASELINE_AUDIT.md`.

