# Day-1 Blocker Classification

## Decision
day1_allowed: false unless blocking_count=0 and manual confirmations complete.
- blocking_count: 3
- requires_manual_acceptance_count: 3

## Blocking Items
- R006 missing_t_plus_1_semantics: Replay/execution adapter evidence exists, but explicit future day-1 T/T+1 acceptance remains incomplete.
- R007 missing_suspension_handling: Market rule evidence exists, but suspension handling is not yet a dedicated day-1 hardening artifact.
- R008 missing_limit_up_down_handling: Market rule evidence exists, but A-share limit up/down handling needs explicit day-1 hardening.

## Requires Manual Acceptance
- R004 missing_adjusted_price_contract: Adjusted price handling exists in data tooling but needs explicit day-1 acceptance wording.
- R014 missing_equity_curve: Equity curve/reporting evidence exists, but forward dry-run use remains unvalidated.
- R018 parameter_data_code_versioning_gap: Versioning exists through release tags and docs, but parameter/data/code binding can be strengthened.

## Deferred Non-Blocking
- R022 no_rl_llm_trading_decision_boundary_gap
- R023 no_auto_promotion_boundary_gap

## Boundary
- classifier only
- run-daily not called
- forward dry-run not started
- main ledger not written
