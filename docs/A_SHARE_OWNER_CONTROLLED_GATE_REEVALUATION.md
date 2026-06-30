# A Share Owner Controlled Gate Reevaluation

v0.8.17 adds a controlled adapter for owner-readiness gate reevaluation.

The adapter reads the v0.8.16 recovery execution package and the preserved v0.8.13 owner-readiness gate decision. It does not run a new owner-readiness gate by default. For `as_of_date=2026-06-26`, the audited decision is `skipped_not_ready`.

Primary artifacts:

- `data/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/controlled_reevaluation_config.json`
- `data/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/reevaluation_readiness_guard.json`
- `data/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/reevaluation_skip_decision.json`
- `data/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/controlled_reevaluation_decision.json`
- `outputs/equity_owner_controlled_gate_reevaluation/daily/2026-06-26/A_SHARE_CONTROLLED_GATE_REEVALUATION.md`

Audited state:

- `source_gate_decision=blocked`
- `readiness_guard_passed=false`
- `reevaluation_allowed=false`
- `reevaluation_skipped=true`
- `controlled_reevaluation_decision=skipped_not_ready`
- `gate_reevaluation_executed=false`
- `new_gate_score_generated=false`
- `new_gate_decision_generated=false`

Boundary:

- no owner-readiness gate rerun
- no `build_from_existing_data` rerun
- no owner daily pack rerun
- no threshold lowering
- no auto or manual waiver approval
- no broker connection, real orders, order preview, or buy/sell signals
- no old `run-daily`
- no official forward dry-run day2 execution

