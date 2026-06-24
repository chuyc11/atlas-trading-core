# Forward Dry-Run Runbook

30 day forward dry-run remains incomplete.

Do not replace forward dry-run with historical replay.

## Daily flow

```bash
python -m trading_core.cli run-daily --date YYYY-MM-DD
python -m trading_core.cli health --date YYYY-MM-DD
python -m trading_core.cli export-summary --date YYYY-MM-DD
python -m trading_core.cli check-consistency --date YYYY-MM-DD
```

## Weekly flow

```bash
python -m trading_core.cli summarize-health --start-date START --end-date END
python -m trading_core.cli audit-dry-run --start-date START --end-date END
python -m trading_core.cli dry-run-validation-report --start-date START --end-date END
```

## Acceptance notes

- Historical replay can support diagnosis, but it is not forward 30d dry-run.
- Price-only replay can validate price-path mechanics, but it is not full global-briefing replay.
- Any forward run must remain virtual and file-backed.
