# A-Share Owner Alert Interpretation

Owner alerts are local monitoring events.

Severity:

- `critical`: fail-close system health or boundary issue.
- `warning`: non-critical health degradation after enough history exists.
- `known_non_blocking`: repeated warning that is known and not currently blocking.
- `informational`: monitoring context, such as insufficient trend history.

Status:

- `triggered`: condition is active.
- `not_triggered`: rule evaluated and condition is inactive.
- `suppressed`: reserved for future suppression logic.
- `insufficient_history`: rule needs more observations before trend evaluation.

For the v0.8.3 release date `2026-06-26`, trend history has one observation. Trend alerts are marked `insufficient_history` and are not counted as triggered alerts.

Alerts should be read as system health prompts only. They are not order plans, broker instructions, real-account actions, or trading advice.
# v0.8.4 remediation interpretation

Owner alerts are inputs to v0.8.4 remediation mapping.

- Critical alert or boundary alert: map to P0 manual review.
- Warning alert: map to P1 safe artifact investigation.
- Known non-blocking alert: map to P2 documentation.
- Insufficient history alert: map to P4 wait-for-history.

The remediation output is a runbook/checklist. It is not a trade instruction, does not execute remediation actions, does not refresh data, does not rerun research workflow, does not place orders, and does not connect broker.
