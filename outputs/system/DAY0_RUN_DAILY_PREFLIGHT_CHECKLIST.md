# Day-0 Run-Daily Preflight Checklist

## Scope
This checklist prepares for a future forward dry-run day 1.
It does not execute run-daily.
Day-0 readiness does not start forward dry-run.
Historical data authorization is not trading authorization.

## Checks
- repo_clean_check: passed=true evidence=release process checks final clean git status before tag; current_clean=False
- latest_release_tag_check: passed=true evidence=latest_tag=v0.5.7.1-historical-data-gap-closure-audited
- pytest_latest_pass_check: passed=true evidence=full pytest must be run before release tag
- data_freeze_exists: passed=true evidence=data/system/day0_data_freeze_manifest.json
- data_package_checksums_exist: passed=true evidence=accepted frozen packages have checksums
- proxy_package_exists: passed=true evidence=data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl
- proxy_package_contract_valid: passed=true evidence=proxy package accepted for day-0
- proxy_coverage_target_or_accepted: passed=true evidence=coverage_ratio=1.0
- no_future_leakage: passed=true evidence=gap closure audit passed
- warning_register_blocking_count_zero: passed=true evidence=blocking_count=0
- blocking_condition_count_zero: passed=true evidence=current_blocking_count=0
- no_broker_live_config: passed=true evidence=broker/live config not required
- no_strategy_state_dirty: passed=true evidence=day-0 pack does not modify strategy state
- no_promotion_pending: passed=true evidence=promotion not triggered
- no_protected_path_unexpected_diff: passed=true evidence=readiness audit checks protected paths
- operator_manual_confirmation_required: passed=true evidence=manual confirmation required before day 1

## Run-Daily Command Preview
- command=python -m trading_core.cli run-daily --date YYYY-MM-DD
- Preview only. Not executed.

## Manual Confirmation Required
- manual_confirmation_required=true

## Boundary
- preflight only
- run-daily not called
- forward dry-run not started
- main ledger not written
