# A Share v0.9.0 Full Regression Plan

- full_pytest_command: `python -m pytest`
- full_pytest_run: False
- full_pytest_required_in_v090: True

## Audit Sweep
- `python -m trading_core.cli audit-a-share-owner-readiness-gate --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-quality-exceptions --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-readiness-recovery --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-readiness-recovery-execution --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-controlled-gate-reevaluation --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-recovery-evidence --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-evidence-backed-reevaluation-prep --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-v0820-gate-outcome --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-closeout-review --as-of-date 2026-06-26`
