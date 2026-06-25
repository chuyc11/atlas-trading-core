# Global Briefing Warning Triage

## Scope
This report triages warnings from v0.5.6 real-package-style integration artifacts.

GB-REAL-FIXTURE is not a production global-briefing package.

## Warning Summary
- warning_count=40
- coverage_ratio=0.6

## Warning Categories
- fixture_expected: 0
- coverage_gap: 3
- pit_ambiguity: 1
- stale_signal_risk: 0
- data_quality: 14
- adapter_limitation: 22
- documentation_only: 0
- unknown: 0

## Production Blockers
- coverage ratio 0.6 is below production minimum 0.8
- high severity point-in-time ambiguity warning present

## Recommended Actions
- fix_package_schema_or_field_values
- inspect_replay_adapter_inputs_and_price_coverage
- raise_min_coverage_for_production_package
- verify_generated_at_timezone_and_decision_time

## Boundary
- triage only
- no replay started
- no run-daily call
- no main ledger write
- no network access
