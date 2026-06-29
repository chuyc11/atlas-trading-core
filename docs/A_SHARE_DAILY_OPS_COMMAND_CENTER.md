# A Share Daily Ops Command Center

v0.8.5 adds a daily ops command center for the A-share research system.

It aggregates existing data refresh, current-day research, owner dashboard, owner monitoring, and owner remediation artifacts into one owner-facing operations control plane.

Boundary:

- v0.8.5 aggregates existing ops artifacts by default
- v0.8.5 does not refresh data by default
- v0.8.5 does not rerun current-day research by default
- v0.8.5 does not execute remediation actions
- v0.8.5 does not generate buy/sell signals
- v0.8.5 does not place orders
- v0.8.5 does not connect broker
- v0.8.5 does not call old run-daily
- v0.8.5 does not execute official forward dry-run day2
- v0.8.5 does not treat ops output as trade instruction
- v0.8.6 should deepen run history and trend baselines
