# A-Share Build Repeatability

v0.8.8 adds `build_from_existing_data` repeatability and diff stability.

It reads the v0.8.7 gated build evidence, snapshots protected paths, repeats the same current-day workflow with `--workflow-mode build_from_existing_data`, snapshots artifacts again, and compares first-build vs second-build outputs.

Outputs:

- `data/equity_build_repeatability/daily/YYYY-MM-DD/`
- `outputs/equity_build_repeatability/daily/YYYY-MM-DD/`
- `data/equity_data_quality/a_share_build_repeatability_audit.json`
- `outputs/audit/A_SHARE_BUILD_REPEATABILITY_AUDIT.md`

Boundary:

- no public network refresh
- no `full_research_run`
- no old run-daily
- no broker
- no real account read
- no real orders
- no order preview
- no buy/sell signals
- no official forward dry-run day2
- repeatability output is not a trade instruction

Recommended next: `v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh`.

## v0.8.9 dashboard handoff

v0.8.9 consumes the repeatability audit, build-vs-build comparison, protected path check, and gated build evidence from v0.8.8/v0.8.7 to refresh the owner dashboard from `build_from_existing_data` outputs.

v0.8.9 does not rerun `build_from_existing_data`, does not refresh public network data, does not run `full_research_run`, does not call old run-daily, and does not treat dashboard output as a trade instruction.
