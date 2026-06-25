# Day-0 Blocking Conditions

## Scope
These conditions define fail-closed gates before a future forward dry-run.
Passing these conditions does not start forward dry-run.
Historical data authorization is not trading authorization.

## Conditions
- missing_critical_price_package: current_status=false evidence=Critical ETF price package is frozen and accepted.
- missing_critical_benchmark_package: current_status=false evidence=Critical benchmark package is frozen and accepted.
- proxy_package_missing: current_status=false evidence=proxy_path=data/global_briefing/normalized/GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1.normalized.jsonl
- proxy_package_invalid_contract: current_status=false evidence=proxy_accepted_for_day0=True
- proxy_coverage_below_0_80: current_status=false evidence=coverage_ratio=1.0
- future_leakage_detected: current_status=false evidence=gap closure future leakage section checked
- unknown_warning_count_above_0: current_status=false evidence=historical warning inventory unknown count checked
- warning_register_has_blocking_items: current_status=false evidence=blocking_count=0
- data_freeze_missing_checksum: current_status=false evidence=all accepted frozen source packages need checksums
- data_freeze_missing_provenance: current_status=false evidence=all accepted source packages need provenance
- run_daily_preflight_failed: current_status=false evidence=preflight generated after this register; checked again by audit
- main_ledger_unexpected_diff: current_status=false evidence=protected path diff checked by readiness audit
- dirty_git_status: current_status=false evidence=release process checks final clean git status before tag
- release_tag_missing: current_status=false evidence=release tag is applied only after readiness audit passes
- protected_path_modified: current_status=false evidence=protected path diff checked by readiness audit
- strategy_state_dirty: current_status=false evidence=day-0 pack does not modify strategy state
- promotion_pending_or_triggered: current_status=false evidence=promotion remains false
- labels_used_in_forward_gate: current_status=false evidence=labels remain false
- ml_shadow_used_in_forward_gate: current_status=false evidence=ML shadow remains false
- experiments_used_in_forward_gate: current_status=false evidence=experiments remain false
- broker_config_detected: current_status=false evidence=broker/live env config not required for day-0 readiness
- live_trading_config_detected: current_status=false evidence=live trading config not required for day-0 readiness
- manual_confirmation_missing: current_status=false evidence=manual confirmation remains required and intentionally incomplete

## Current Blocking Count
- current_blocking_count=0

## Manual Confirmation Required
- manual_confirmation_still_required=true

## Boundary
- conditions only
- forward dry-run not started
- run-daily not called
- main ledger not written
