# Forward Dry-Run Day-0 Readiness

v0.5.8 adds the day-0 operational readiness pack for a future 30 trading-day forward dry-run.

Day-0 readiness does not start forward dry-run. `run-daily` is not called. Manual confirmation remains incomplete by default.

## Commands

```powershell
python -m trading_core.cli day0-data-freeze
python -m trading_core.cli day0-warning-register
python -m trading_core.cli day0-blocking-conditions
python -m trading_core.cli day0-run-daily-preflight
python -m trading_core.cli day0-manual-confirmation-packet
python -m trading_core.cli forward-dry-run-operating-calendar
python -m trading_core.cli day0-readiness-report
python -m trading_core.cli audit-day0-readiness
```

## Accepted Limitations

- EPU remains partial; `us_epu` and `europe_epu` are missing, and policy uncertainty may be proxied.
- OECD macro-cycle input may be an authorized macro-cycle proxy and is not official OECD CLI.
- Internal global-briefing historical package remains `not_configured`.
- Proxy package is not an internal global-briefing signal.

## Explicit Non-Claims

- Historical data authorization is not trading authorization.
- Day-0 readiness is not forward dry-run validation.
- Day-0 readiness is not strategy effectiveness proof.
- Day-0 readiness is not live trading readiness.

## Boundary

- forward dry-run not started
- run-daily not called
- manual confirmation complete: false
- main ledger not written
- labels, ML shadow, experiments, and promotion not used
- no broker/live/RL/LLM trading decision added

## v0.5.8.1 Follow-Up

The v0.5.8.1 plan alignment and MVP gap audit reviews whether current implementation evidence satisfies the MVP plan before any future day 1. Plan alignment is an audit, not day 1 authorization.

It keeps the same operational boundary: forward dry-run not started, `run-daily` not called, main ledger not written, historical performance not treated as strategy effectiveness proof, ML shadow not used as authorization, LLM not used for trading decision, RL not used, and promotion not triggered.

## v0.6.2 Follow-Up

v0.6.2 creates the forward dry-run start authorization pack after daily workflow binding. It does not start forward dry-run, does not call run-daily, and does not write the main ledger.

Release defaults remain fail-closed:

- `manual_confirmation_complete=false`
- `forward_dry_run_start_authorized=false`
- `day1_start_allowed=false`
- `day1_prompt_eligible=false`
- `day1_prompt_generated=false`

The only allowed next action after the v0.6.2 pack is owner manual confirmation.
