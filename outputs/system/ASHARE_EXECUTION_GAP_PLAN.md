# A-Share Execution Gap Plan

## Scope
This plan targets execution-rule blockers identified by v0.5.8.1.
It does not start forward dry-run.
v0.5.9 hardens virtual execution rules but does not start forward dry-run.

## Baseline Day-1 Blockers
- baseline_day1_blocker_count: 3

## Work Items
- missing_t_plus_1_semantics: targeted
- missing_suspension_handling: targeted
- missing_limit_up_down_handling: targeted

## Boundary
- planning only
- run-daily not called
- forward dry-run not started
- main ledger not written
