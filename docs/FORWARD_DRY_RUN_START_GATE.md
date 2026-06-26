# Forward Dry-Run Start Gate

The v0.6.2 start gate validator determines whether a future day1 start is allowed. The release default is fail-closed.

## Release Default

- `manual_confirmation_complete=false`
- `forward_dry_run_start_authorized=false`
- `day1_start_allowed=false`
- deny reasons include `manual_confirmation_complete=false` and `forward_dry_run_start_authorized=false`

## Run-Daily Preview

The run-daily command preview is metadata only. It records the future command string, `preview_only=true`, `executed=false`, and `run_daily_called=false`. It is not instructions to execute day1.

## Boundary

- v0.6.2 creates an authorization pack only and does not start forward dry-run
- run-daily not called
- run-daily not executed
- forward dry-run not started
- main ledger not written
- no broker connected
- no ML/LLM/RL trading decision
- promotion not triggered

## v0.6.2.1 Revalidation

After owner manual confirmation is materialized, the v0621 gate reports:

- `technical_prerequisites_passed=true`
- `manual_confirmation_complete=true`
- `forward_dry_run_start_authorized=true`
- `day1_prompt_eligible=true`
- `day1_start_allowed=false`
- deny reason: `day1_execution_requires_separate_prompt`

The gate still does not start forward dry-run day 1 and does not call run-daily.
