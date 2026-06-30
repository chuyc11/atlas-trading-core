# A-Share Owner Daily Pack Audit

The v0.8.11 audit command:

```bash
python -m trading_core.cli audit-a-share-owner-daily-pack --as-of-date 2026-06-26
```

It writes:

- `data/equity_data_quality/a_share_owner_daily_pack_audit.json`
- `outputs/audit/A_SHARE_OWNER_DAILY_PACK_AUDIT.md`

The audit checks:

- all required JSON artifacts exist
- all required Markdown reports exist
- v0.8.10 build-output ops refresh audit passed
- v0.8.9 build-output dashboard audit passed
- v0.8.8 repeatability audit passed
- v0.8.7 gated build audit passed
- `source_workflow_mode=build_from_existing_data`
- `business_output_drift_count=0`
- `protected_path_modifications_detected=false`
- `automatic_action_count=0`
- `execute_remediation_actions=false`
- `external_notifications_sent=false`
- owner decision pack is operations-only
- no forbidden operational decision categories
- no forbidden safe action types
- source trace is complete and hashes match
- boundary fields remain clean
- no forbidden artifacts or positive trading wording are present

Audit mode is fail-closed and does not rebuild the pack, rerun `build_from_existing_data`, refresh data, execute remediation, send notifications, connect broker, place orders, or create signals.
