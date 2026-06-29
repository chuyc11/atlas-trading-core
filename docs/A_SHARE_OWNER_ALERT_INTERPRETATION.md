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
