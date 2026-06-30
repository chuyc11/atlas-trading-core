# A-Share Owner Daily Pack History

v0.8.12 adds append-only owner daily pack history.

It reads the v0.8.11 owner daily pack artifacts and writes:

- `data/equity_owner_daily_pack_history/daily/YYYY-MM-DD/`
- `data/equity_owner_daily_pack_history/history/`
- `outputs/equity_owner_daily_pack_history/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_owner_daily_pack_history_audit.json`
- `outputs/audit/A_SHARE_OWNER_DAILY_PACK_HISTORY_AUDIT.md`

History rules:

- append-only by default
- deduplicate by `as_of_date + source_workflow_mode + daily_pack_manifest_sha256`
- exact duplicate append is idempotent
- same date with changed content is recorded as a warning
- no synthetic history
- no future dates
- no fabricated trends

The release observation count is 1, below the default minimum of 5, so trend analysis is marked `insufficient_history`.
