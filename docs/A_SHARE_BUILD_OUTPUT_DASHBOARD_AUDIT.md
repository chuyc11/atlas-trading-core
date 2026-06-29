# A-Share Build Output Dashboard Audit

Run:

```bash
python -m trading_core.cli audit-a-share-build-output-owner-dashboard --as-of-date 2026-06-26
```

The audit checks:

- v0.8.8 repeatability audit passed
- v0.8.7 gated build audit passed
- v0.8.2 validate-source dashboard audit passed
- v0.8.0 data refresh audit passed
- `source_workflow_mode=build_from_existing_data`
- `business_output_drift_count=0`
- protected path modifications are absent
- required cards exist
- required validate fallback was not used
- source trace is complete and required source hashes match
- boundary is clean

The audit is fail-close and does not rebuild the dashboard.

