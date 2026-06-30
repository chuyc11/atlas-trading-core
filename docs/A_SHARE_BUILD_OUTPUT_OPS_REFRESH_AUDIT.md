# A Share Build Output Ops Refresh Audit

Run:

```bash
python -m trading_core.cli audit-a-share-build-output-ops-refresh --as-of-date 2026-06-26
```

The audit is fail-close. It checks required JSON artifacts, Markdown reports, input audits, build-output source mode, comparison completion, source trace, boundary fields, forbidden artifacts, forbidden positive wording, and that no automatic or external action was executed.

The audit does not rebuild refresh artifacts, rerun workflows, refresh data, execute remediation, connect broker, or place orders.

