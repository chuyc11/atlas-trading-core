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

## v0.6.3.2 Day1 Owner Report Pack

Run only after v0.6.3 and v0.6.3.1 artifacts exist:

```bash
python -m trading_core.cli forward-dry-run-day1-owner-report-scope-plan
python -m trading_core.cli forward-dry-run-day1-owner-summary-report
python -m trading_core.cli forward-dry-run-day1-strategy-signal-explanation
python -m trading_core.cli forward-dry-run-day1-virtual-order-fill-report
python -m trading_core.cli forward-dry-run-day1-isolated-ledger-report
python -m trading_core.cli forward-dry-run-day1-data-reproducibility-appendix
python -m trading_core.cli forward-dry-run-day1-continuation-blocker-note
python -m trading_core.cli forward-dry-run-day1-owner-report-pack-summary
python -m trading_core.cli audit-forward-dry-run-day1-owner-report-pack
```

This generates owner-facing day1 reports only. It does not execute day2, does not execute day3, does not call run-daily, does not download real-time market data, does not call external APIs, does not write the main ledger, does not connect a broker, and does not place real orders. Day2 is blocked because local market, benchmark, and risk proxy data do not extend beyond `2026-06-25`. Recommended next version: `v0.6.3.3-forward-dry-run-data-horizon-extension`.
