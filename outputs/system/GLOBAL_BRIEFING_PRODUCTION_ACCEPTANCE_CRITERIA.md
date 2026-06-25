# Global Briefing Production Package Acceptance Criteria

## Scope
This document defines criteria for future production historical global-briefing package acceptance.

It does not accept any package by itself.

## Required Minimums
- min coverage >= 0.80
- target coverage >= 0.90
- future signal leakage rows = 0
- high severity PIT issues = 0
- unknown warnings = 0

## Required Audits
- signal_contract_validation
- package_coverage_audit
- point_in_time_audit
- isolated_replay_workflow
- integration_audit
- evidence_quality_report

## Explicit Non-Claims
- package acceptance does not prove strategy effectiveness
- package acceptance does not validate forward dry-run
- package acceptance does not certify live trading readiness

## Boundary
- criteria only
- no replay started
- no main ledger write
- no run-daily call
