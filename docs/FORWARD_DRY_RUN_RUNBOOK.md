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

## v0.6.3.1 Day1 Continuation Artifacts

Run only after v0.6.3 day1 execution is audited:

```bash
python -m trading_core.cli forward-dry-run-day1-continuation-gap-analysis
python -m trading_core.cli forward-dry-run-day1-artifact-manifest
python -m trading_core.cli forward-dry-run-day1-reproducibility-manifest
python -m trading_core.cli forward-dry-run-day2-readiness-packet
python -m trading_core.cli forward-dry-run-day2-continuation-gate-preview
python -m trading_core.cli audit-forward-dry-run-day1-continuation-artifacts
python -m trading_core.cli reclassify-day1-continuation-artifacts-v0631
```

This prepares the next v0.6.4 attempt by creating day1-derived continuation artifacts. It does not execute day2, does not call run-daily, and does not write the main ledger.
