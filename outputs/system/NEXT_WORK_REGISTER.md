# Next Work Register

## Recommended Next Version
v0.5.9-ashare-execution-rules-hardening

## Rationale
A-share execution rule blockers remain before day 1.

## Work Items
- v0.5.9 t_day_signal_t_plus_1_execution: required_before_day1=true
- v0.5.9 suspension_handling: required_before_day1=true
- v0.5.9 limit_up_limit_down_handling: required_before_day1=true

## Boundary
- register only
- run-daily not called
- forward dry-run not started
- main ledger not written
