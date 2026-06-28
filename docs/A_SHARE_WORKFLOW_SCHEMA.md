# A-Share Workflow Schema

v0.7.9 workflow artifacts are JSON-first and audit-readable.

## Config

`workflow_config.json` records:

- `config_id`
- `target_version`
- `as_of_date`
- `mode`
- allowed modes
- public data refresh flag
- latest artifact date flag
- timestamp drift policy
- old run-daily disabled
- day2 disabled
- broker disabled
- real orders disabled
- research and virtual-only flags

## Stage Manifest

`workflow_stage_manifest.json` contains the 11 required stages:

- `stage_00_preflight`
- `stage_01_data_readiness`
- `stage_02_tradable_universe`
- `stage_03_feature_engineering`
- `stage_04_scoring`
- `stage_05_candidate_generation`
- `stage_06_virtual_portfolio_construction`
- `stage_07_daily_briefing`
- `stage_08_virtual_portfolio_tracking`
- `stage_09_workflow_audit`
- `stage_10_owner_summary`

Each stage records `stage_id`, `stage_name`, `stage_order`, `mode`, `command`, timestamps, duration, status, input artifacts, output artifacts, audit artifacts, blocking reasons, warnings, skipped reason, and boundary flags.

Status values:

- `passed`
- `failed`
- `skipped`
- `blocked`
- `not_run`

## Run Manifest

`workflow_run_manifest.json` records run timing, overall pass/fail, warnings, blocking reasons, stages, input versions, boundary flags, and `build_timestamp_non_strict_idempotency=true`.

## Source Trace

`workflow_source_trace.json` records upstream manifests, upstream audits, workflow manifests, stage commands, hashes where available, source completeness, and forbidden path hits.

Forbidden source paths include external research, sample/mock paths, day_002/day_003 paths, broker/order/trade/account paths, and old run-daily paths.

## Boundary Check

`workflow_boundary_check.json` records orchestration-only status and verifies no forbidden workflow artifacts were produced.
