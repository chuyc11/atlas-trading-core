# Command Cookbook

This cookbook is for resuming the research-only workbench. It does not authorize live trading.

## Resume project

```bash
git status
git tag --points-at HEAD
python -m pytest
```

## Find reports

```bash
python -m trading_core.cli quick-status
python -m trading_core.cli report-index
python -m trading_core.cli latest-artifact --type all
python -m trading_core.cli latest-artifact --type handoff
python -m trading_core.cli artifact-browser
```

## Check safety

```bash
python -m trading_core.cli boundary-regression-audit
python -m trading_core.cli system-integrity-audit
python -m trading_core.cli forward-dry-run-readiness
python -m trading_core.cli audit-global-briefing-replay
```

## Run reporting pipeline

```bash
python -m trading_core.cli run-research-pipeline --start-date START --end-date END
```

## Run global-briefing historical replay harness

```bash
python -m trading_core.cli global-briefing-contract
python -m trading_core.cli validate-global-briefing-signals --input tests/fixtures/global_briefing/signals_valid.jsonl --start-date 2024-01-02 --end-date 2024-01-08
python -m trading_core.cli build-global-briefing-replay-bundle --signals tests/fixtures/global_briefing/signals_valid.jsonl --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08 --allow-carry-forward
python -m trading_core.cli replay-global-briefing-history --bundle data/replays/global_briefing/replay_bundle-2024-01-02-2024-01-08.json --prices tests/fixtures/global_briefing/prices_valid.csv --start-date 2024-01-02 --end-date 2024-01-08
python -m trading_core.cli global-briefing-replay-report --replay data/replays/global_briefing/global_briefing_replay-2024-01-02-2024-01-08.json
python -m trading_core.cli audit-global-briefing-replay
```

The global-briefing replay harness is isolated historical replay only. It is not forward dry-run validation, not live trading readiness, and not strategy effectiveness proof.

## What not to do

* do not run live trading
* do not treat shadow as active
* do not use historical replay as forward dry-run
* do not use reports as admission gate
* do not treat global-briefing replay artifacts as broker or promotion output

## Boundary

* This project remains research-only.
* This system is not live-ready.
* Forward 30d dry-run is not completed.
* Global-briefing historical replay is isolated and writes no main ledger.
