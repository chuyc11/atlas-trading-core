# Forward Dry-Run 30 Trading-Day Plan

## 1. Scope
This plan prepares a 30 trading-day virtual forward dry-run.
It does not start or validate the dry-run.

## 2. Daily Commands

For each trading day:

```bash
python -m trading_core.cli run-daily --date YYYY-MM-DD
python -m trading_core.cli health --date YYYY-MM-DD
python -m trading_core.cli export-summary --date YYYY-MM-DD
python -m trading_core.cli check-consistency --date YYYY-MM-DD
```

## 3. Weekly Commands

```bash
python -m trading_core.cli summarize-health --start-date START --end-date END
python -m trading_core.cli audit-dry-run --start-date START --end-date END
python -m trading_core.cli dry-run-validation-report --start-date START --end-date END
python -m trading_core.cli weekly-research-report --start-date START --end-date END --include-experiments --include-ml-shadow --include-mistakes
```

## 4. End-of-Run Commands

```bash
python -m trading_core.cli dry-run-validation-report --start-date START --end-date END
python -m trading_core.cli monthly-research-report --start-date START --end-date END --include-weekly --include-experiments --include-ml-shadow
python -m trading_core.cli final-handoff-review
```

## 5. What This Is Not

* not live trading
* not broker execution
* not strategy effectiveness proof
* not historical replay
* not global-briefing full replay

## 6. Planned Dates

Trading calendar not found. Plan uses placeholders and requires manual calendar confirmation.
