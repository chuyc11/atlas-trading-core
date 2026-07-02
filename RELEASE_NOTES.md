# Release Notes

## v1.1.0-a-share-owner-ops-autonomous-simulation-platform-expansion

v1.1.0 expands the A-share research-only and simulation-only platform into an owner-ops operating layer for daily review, governance, monitoring, and simulated lifecycle management.

- adds v1.1 owner command center JSON and Chinese owner reports
- integrates v1.0.1 benchmark coverage and performance claim guard into owner-facing ops artifacts
- adds daily workflow integration, history, evidence accumulation, artifact integrity, and safety boundary sweeps
- adds simulated account reconciliation, virtual broker lifecycle checks, paper ledger invariant checks, commission/slippage attribution, turnover, and anomaly monitoring
- expands experiment and strategy registry governance with lineage, status transition audit, rejected/rollback registers, cooldown tracking, and promotion eligibility explanation
- adds LLM proposal governance and RL simulated lab governance, both simulation-only and unable to create trade instructions or real orders
- adds shadow/canary/simulated-active lifecycle governance plus simulated promotion, demotion, replacement, rejection, cooldown, and rollback workflows
- adds local/internal monitoring alerts and remediation checklist generation
- preserves owner-readiness as blocked at 54 / 75 / gap 21
- does not connect broker, read real accounts, place real orders, generate order previews, generate buy/sell signals, run owner-readiness gate, or claim live trading readiness
- full pytest: `1843 passed, 1 skipped`
- recommended next version: `v1.1.1-a-share-local-post-close-operator-scheduling-and-runbook-hardening`

## v1.0.1-a-share-benchmark-data-and-performance-claim-hardening

v1.0.1 hardens A-share benchmark data attribution and performance claim safety without adding trading functionality.

- adds benchmark source registry and coverage matrix for CSI300, CSI500, CSI1000, cash, and equal-weight tradable-universe benchmarks
- generates zero-return cash baseline with explicit simulation-only assumptions
- builds equal-weight universe benchmark from local data when supported, otherwise fails safely
- records missing CSI benchmark data without fabricating excess return, tracking error, or relative drawdown
- adds performance claim guard blocking real performance, live trading, investment advice, and unverified benchmark-relative claims
- generates owner-facing Chinese benchmark limitation and claim guard reports
- preserves owner-readiness as blocked at 54 / 75 / gap 21
- does not execute owner-readiness gate or controlled gate reevaluation
- does not connect broker, read real accounts, place real orders, generate order previews, or generate buy/sell signals
- full pytest run remains deferred until next major closeout or explicit request
- recommended next version: `v1.0.2-a-share-owner-dashboard-benchmark-integration-and-report-polish`

## v1.0.0-a-share-autonomous-simulation-platform-release

v1.0.0 officially releases trading-core as an A-share autonomous research and simulation platform.

- releases the platform as research-only and simulation-only
- verifies v1.0.0-prep readiness decision `ready_for_v100_release`
- reuses the v1.0.0-prep full regression result: `1807 passed, 1 skipped, 0 failed`
- generates final release decision `released_as_research_only_simulation_platform`
- records final scope, safety boundary, known limitations, release summary, and release audit
- preserves owner-readiness as blocked at 54 / 75 / gap 21
- keeps `owner_operationally_acceptable=false`
- keeps benchmark/index attribution warning visible and blocks real performance claims
- does not execute owner-readiness gate or controlled gate reevaluation
- does not generate a new readiness score or gate decision
- does not connect broker, read real account data, place real orders, generate real order previews, or generate buy/sell signals
- does not call old run-daily or execute official forward dry-run day2
- does not claim live trading readiness
- recommended next version: `v1.0.1-a-share-benchmark-data-and-performance-claim-hardening`

## v1.0.0-prep-a-share-autonomous-simulation-platform-closeout

v1.0.0-prep closes out the A-share autonomous research and simulation platform for v1.0 release readiness without adding new product features.

- verifies the v0.9.8 autonomous simulation platform baseline and required artifacts
- classifies both v0.9.8 benchmark/attribution warnings as non-blocking for v1.0.0 release readiness
- runs full regression with `1807 passed, 1 skipped, 0 failed`
- verifies CLI surface, artifact integrity, and safety boundaries
- records `release_readiness_decision=ready_for_v100_release`
- preserves owner-readiness as blocked at 54 / 75 / gap 21
- keeps `owner_operationally_acceptable=false`
- does not execute owner-readiness gate
- does not execute controlled gate reevaluation
- does not generate a new owner-readiness score or gate decision
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate real order previews or buy/sell signals
- does not call old run-daily
- does not execute official forward dry-run day2
- does not claim live trading readiness
- recommended next version: `v1.0.0-a-share-autonomous-simulation-platform-release`

## v0.9.8-a-share-v09-autonomous-research-and-simulation-platform-completion

v0.9.8 completes the A-share v0.9 product as a research-only and simulation-only autonomous research platform.

- adds post-close daily platform runner with dry-run and simulation-only modes
- adds simulated account state, simulated order intents, virtual broker simulated fills, paper ledger, commission/slippage, and turnover summaries
- adds benchmark/attribution summary with honest warning when benchmark data is missing
- adds Chinese owner command center with explicit research-only and simulation-only wording
- adds local monitoring alerts and evidence auto-accumulation records
- adds experiment registry, strategy registry, deterministic LLM research proposal register, automated experiment result, RL simulated strategy lab, and shadow/canary promotion evaluation
- keeps all platform artifacts marked research-only, simulation-only, virtual-only, not investment advice, not real order, not order preview, not buy/sell signal, and not live trading ready
- preserves owner-readiness blocked state
- does not execute owner-readiness gate
- does not execute controlled reevaluation
- does not generate new owner-readiness score or decision
- does not connect broker
- does not read real account data
- does not place orders
- does not generate real order previews or buy/sell signals
- does not call old run-daily
- does not execute official forward dry-run day2
- does not silently install scheduler or daemon
- does not run full pytest
- recommended next version: `v1.0.0-prep-a-share-autonomous-simulation-platform-closeout`

## v0.9.7-a-share-historical-evidence-backfill-and-post-close-refresh-planning

v0.9.7 extends the A-share evidence window before 2026-06-26, attempts local historical research-only backfill, recomputes evidence readiness, and adds post-close public-data-only refresh planning.

- extends historical evidence window before 2026-06-26
- discovers actual A-share trading days from local calendar
- reuses existing eligible evidence days 2026-06-26 and 2026-07-01
- attempts backfill for missing historical research-only outputs where local data is available
- records failed historical backfill days honestly without fabricating target evidence count
- recomputes evidence quality and blocker coverage after backfill
- generates go/no-go after historical backfill
- adds post-close public-data-only refresh planning for A-share trading days
- recommends 15:45 Asia/Shanghai for manual post-close refresh planning
- does not silently install scheduler or daemon
- preserves owner-readiness blocked state
- does not execute owner-readiness gate
- does not execute controlled reevaluation
- does not generate new owner-readiness score or decision
- does not connect broker
- does not read real account data
- does not place orders
- does not generate order previews or buy/sell signals
- does not call old run-daily
- does not execute official forward dry-run day2
- does not run full pytest
- recommended next version: `v0.9.8-a-share-reevaluation-readiness-closeout-after-backfill`

## v0.9.6-a-share-controlled-readiness-reevaluation-or-final-not-ready-closeout

v0.9.6 closes out the v0.9.5 no-go state by selecting the final not-ready branch and materializing an owner/developer evidence plan without executing controlled reevaluation.

- selects `final_not_ready_closeout` from the v0.9.5 `no_go_additional_evidence_required` baseline
- records controlled reevaluation disallowance and preserves `controlled_reevaluation_allowed=false`
- generates final not-ready closeout result, source evidence review, branch selection, unresolved blocker summary, owner not-ready summary, and developer follow-up backlog
- generates additional evidence requirement register and next-cycle evidence plan
- keeps owner-readiness blocked at 54 / 75 / gap 21
- keeps blocker coverage at 0.5 and requires at least 3 additional research-only evidence days
- preserves all unresolved blockers as open
- does not run controlled reevaluation or owner-readiness gate
- does not generate a new score or gate decision
- does not lower thresholds or record a waiver
- does not refresh data or rerun the research pipeline
- does not connect broker, read real account data, place orders, generate order previews, or generate buy/sell signals
- does not call old run-daily
- does not execute official forward dry-run day2
- does not run full pytest
- recommended next version: `v0.9.7-a-share-additional-evidence-collection-plan-execution-tracker`

## v0.9.5-a-share-research-evidence-accumulation-quality-review-and-reevaluation-prep

v0.9.5 adds A-share research evidence accumulation, quality review, and controlled reevaluation prep without executing the gate.

- builds multi-day research output evidence package from existing local artifacts
- inventories v0.9.3 data freshness and v0.9.4 research pipeline outputs
- registers evidence-eligible research output days
- validates output completeness across dates
- adds candidate overlap and turnover diagnostics with research-only wording
- adds score distribution diagnostics marked not trade signals and not owner-readiness score
- adds virtual-only portfolio research diagnostics
- adds research briefing quality diagnostics
- adds research-only boundary validation
- adds readiness evidence gap analysis
- adds evidence quality scorecard
- adds blocker evidence mapping
- adds reevaluation input candidate package without executing gate
- adds controlled reevaluation precheck without rerunning gate
- adds go/no-go decision for future reevaluation prep
- adds not-ready reason register when evidence is insufficient
- preserves owner-readiness blocked state
- does not refresh data
- does not rerun research pipeline
- does not rerun owner-readiness gate
- does not execute controlled gate reevaluation
- does not generate new owner-readiness score or decision
- does not connect broker
- does not read real account data
- does not place orders
- does not generate order previews or buy/sell signals
- does not call old run-daily
- does not execute official forward dry-run day2
- does not run full pytest
- recommended next version: `v0.9.6-a-share-controlled-readiness-reevaluation-or-final-not-ready-closeout`

## v0.9.4-a-share-research-pipeline-rerun-from-refreshed-data

v0.9.4 reruns the A-share research-only pipeline from the v0.9.3 refreshed `2026-07-01` source data and records an auditable control pack.

- adds `rerun-a-share-research-pipeline-from-refreshed-data`
- generates features, research scores, research candidates, virtual-only portfolios, and research briefing outputs for `2026-07-01`
- writes the required v0.9.4 JSON control artifacts and owner-facing markdown result
- preserves v0.9.3 `missing_quote_symbol_count=355` as a non-blocking warning
- records available-window research rerun warning `research_rerun_available_window_min_effective_trading_days_20d=17`
- keeps owner-readiness blocked at 54 / 75 / gap 21
- does not rerun owner-readiness gate or controlled reevaluation
- does not generate a new gate score or decision
- does not connect broker, read real account data, place orders, generate order previews, or generate buy/sell signals
- does not run full pytest
- recommended next version: `v0.9.5-a-share-multi-day-research-output-evidence-accumulation`

## v0.9.3-a-share-data-freshness-refresh

v0.9.3 refreshes public A-share research data to the latest resolved available date and records a compact freshness package for `2026-07-01`.

- records provider status, coverage summary, refresh result, boundary check, and manifest
- shows staleness before and after refresh
- refreshes public market research data only
- does not rerun research pipeline
- does not rerun `build_from_existing_data`
- does not rerun owner-readiness gate
- does not generate a new gate score or decision
- does not connect broker
- does not read real account data
- does not place orders
- does not generate order previews or buy/sell signals
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not run full pytest
- recommended next version: `v0.9.4-a-share-research-pipeline-rerun-from-refreshed-data`

## v0.9.2-a-share-owner-daily-runbook-cli-entry-and-staleness-awareness

v0.9.2 is a scoped stop-bleed release that adds a read-only owner-facing daily status CLI:

```powershell
python -m trading_core.cli owner-daily-status --as-of-date 2026-06-26
```

- prints an owner-readable daily status summary
- supports `--format text` and `--format json`
- shows known blocked owner-readiness state
- shows readiness score 54 / threshold 75 / gap 21
- shows v0.9.0 full pytest and audit sweep status
- shows data staleness without refreshing data
- does not generate data or output artifacts
- does not add docs
- does not rerun owner-readiness gate
- does not generate a new gate score or decision
- does not refresh data
- does not connect broker
- does not place orders
- does not generate order previews or buy/sell signals
- does not run full pytest
- recommended next version: `v0.9.3-a-share-data-freshness-refresh`

## v0.9.1-a-share-owner-daily-run-operator-experience-and-known-blocked-state-hardening

v0.9.1 adds an owner/operator status usability layer around the v0.9.0 known blocked owner-readiness state.

Adds:

- operator experience config, input availability, source resolution, and date alignment
- owner daily status card
- known blocked state banner and explanation
- operator capability matrix and safe action menu
- artifact navigation index
- owner next-step decision aid
- RC status summary
- audit and test status summary
- safety boundary status panel
- unresolved blocker digest
- operator source trace, boundary check, manifest, summary, reports, and audit

Audited result for `as_of_date=2026-06-26`:

- operator experience audit overall_passed=true
- blocking_reasons=[]
- source_release_candidate=`v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression`
- known_owner_readiness_state=blocked
- owner_operationally_acceptable=false
- readiness_score=54
- minimum_owner_readiness_score=75
- score_gap=21
- v090_full_pytest_passed=true
- v090_audit_sweep_passed=true
- targeted_pytest_passed=true
- targeted_pytest_count=21
- full_pytest_run=false
- full_pytest_deferred_until=next-major-closeout-or-explicit-request

Boundary:

- preserves blocked owner-readiness state and does not claim owner-readiness passed
- does not generate a new gate score or decision
- does not rerun owner readiness gate, `build_from_existing_data`, or owner daily pack
- does not execute full pytest by default
- does not lower readiness thresholds or auto-waive quality gates
- does not refresh public network data or run `full_research_run`
- does not execute remediation actions or send external notifications
- does not generate buy/sell signals or order previews
- does not connect broker, read real accounts, place real orders, call old `run-daily`, or execute official forward dry-run day2
- does not treat operator status as trade instruction
- recommended next version: `v0.9.2-a-share-owner-daily-status-artifact-navigation-and-report-usability`

## v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression

v0.9.0 executes the A-share owner-readiness closeout release candidate and full regression for `as_of_date=2026-06-26`.

Adds:

- v0.9.0 RC input validation
- full pytest result capture for `python -m pytest`
- v0.8.13-v0.8.21 audit sweep
- boundary and source-trace sweeps
- documentation freeze check
- known blocked owner-readiness disclosure
- release-candidate decision and owner summary
- v0.9.0 source trace, boundary check, manifest, reports, and audit

Audited result:

- full_pytest_run=true
- full_pytest_command=`python -m pytest`
- full_pytest_result=`1701 passed, 1 skipped in 907.53s`
- audit_sweep_passed=true
- boundary_sweep_passed=true
- source_trace_sweep_passed=true
- documentation_freeze_passed=true
- source_gate_decision=`blocked`
- owner_operationally_acceptable=false
- previous_readiness_score=54
- minimum_owner_readiness_score=75
- score_gap=21
- release_candidate_decision=`v090_rc_passed_with_known_blocked_owner_readiness`
- recommended next version: `v0.9.1-a-share-owner-daily-run-operator-experience-and-known-blocked-state-hardening`

Boundary:

- preserves known blocked owner-readiness state
- does not rerun owner readiness gate
- does not generate a new gate score or decision
- does not lower readiness thresholds or auto-waive gates
- does not rerun `build_from_existing_data`, owner daily pack, public refresh, or `full_research_run`
- does not execute remediation actions or send external notifications
- does not generate buy/sell signals, order previews, broker connection, account reads, or real orders
- does not call old `run-daily` or execute official forward dry-run day2
- treats v0.9.0 as research-only release evidence, not a trade instruction

## v0.8.21-a-share-owner-readiness-closeout-review-and-v0.9.0-rc-prep

v0.8.21 A-share owner-readiness closeout review and v0.9.0 RC prep.

Adds:

- closeout review config
- closeout input availability
- closeout source resolution
- closeout date alignment
- v0.8.13-to-v0.8.20 lineage review
- blocked decision lineage
- readiness score lineage
- evidence insufficiency lineage
- final blocked closeout review
- unresolved blocker register
- v0.9.0 RC scope proposal
- v0.9.0 full regression plan
- v0.9.0 audit sweep plan
- v0.9.0 documentation freeze checklist
- v0.9.0 release risk register
- v0.9.0 release candidate readiness decision
- closeout source trace
- closeout boundary check
- closeout manifest
- owner-facing closeout review reports
- closeout review audit

Audited result for `as_of_date=2026-06-26`:

- closeout review audit overall_passed=true
- audit blocking reasons: none
- selected_v0820_branch=final_blocked_closeout
- source_gate_decision=blocked
- previous_readiness_score=54
- minimum_owner_readiness_score=75
- score_gap=21
- owner_operationally_acceptable=false
- blocked_state_intentional=true
- blocked_state_audited=true
- blocked_state_misrepresented_as_acceptable=false
- new_gate_score_generated=false
- new_gate_decision_generated=false
- execute_full_pytest=false
- v090_rc_scope_generated=true
- v090_full_regression_plan_generated=true
- v090_audit_sweep_plan_generated=true
- v090_documentation_freeze_checklist_generated=true
- v090_release_risk_register_generated=true
- v090_release_candidate_readiness_decision=ready_with_known_blocked_owner_readiness_state
- unresolved_blocker_count=7
- blockers_that_block_owner_readiness_acceptance=6
- blockers_that_block_v090_rc=0

Boundary:

- does not rerun owner readiness gate
- does not generate a new gate score
- does not generate a new gate decision
- preserves final blocked closeout
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat closeout review as trade instruction
- does not execute full pytest
- uses targeted pytest only for small version validation
- prepares v0.9.0 full regression and audit sweep
- recommended next version: `v0.9.0-a-share-owner-readiness-closeout-rc-and-full-regression`

## v0.8.20-a-share-owner-readiness-controlled-gate-reevaluation-or-final-blocked-closeout

v0.8.20 A-share owner-readiness controlled gate reevaluation or final blocked closeout.

Adds:

- v0.8.20 outcome config
- v0.8.20 input availability
- v0.8.20 source resolution
- v0.8.20 date alignment
- branch decision
- controlled gate reevaluation outcome
- final blocked closeout
- threshold preservation check
- waiver exclusion check
- boundary preservation check
- owner outcome summary
- v0.8.20 source trace
- v0.8.20 boundary check
- v0.8.20 manifest
- owner-facing v0.8.20 outcome reports
- v0.8.20 outcome audit

Audited result for `as_of_date=2026-06-26`:

- v0.8.20 outcome audit overall_passed=true
- audit blocking reasons: none
- selected_branch=final_blocked_closeout
- branch_decision_consistent=true
- controlled_reevaluation_allowed=false
- controlled_reevaluation_executed=false
- final_blocked_closeout_generated=true
- source_gate_decision=blocked
- previous_readiness_score=54
- minimum_owner_readiness_score=75
- new_controlled_readiness_score_generated=false
- new_controlled_readiness_score=null
- new_controlled_readiness_grade=null
- new_controlled_gate_decision_generated=false
- new_controlled_gate_decision=null
- owner_operationally_acceptable=false
- threshold_lowered=false
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- waiver_used_for_outcome=false
- recommended next version: `v0.8.21-a-share-owner-readiness-closeout-review-and-v0.9.0-rc-prep`

Boundary:

- executes controlled gate reevaluation only if v0.8.19 evidence is eligible
- otherwise finalizes blocked closeout
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat gate outcome as trade instruction
- uses targeted pytest only for small version validation
- defers full pytest to `v0.9.0-or-big-version-closeout`

## v0.8.19-a-share-owner-readiness-evidence-backed-gate-reevaluation-prep

v0.8.19 A-share owner-readiness evidence-backed gate reevaluation prep.

Adds:

- evidence-backed prep config
- evidence-backed prep input availability
- evidence-backed prep source resolution
- evidence-backed prep date alignment
- evidence sufficiency for reevaluation decision
- evidence-to-gate mapping
- reevaluation input package
- score impact readiness summary
- gate threshold preservation package
- waiver exclusion package
- boundary preservation package
- evidence-backed readiness checklist
- remaining evidence gap decision
- controlled reevaluation eligibility decision
- next gate reevaluation execution plan
- evidence-backed prep source trace
- evidence-backed prep boundary check
- evidence-backed prep manifest
- owner-facing evidence-backed prep reports
- evidence-backed prep audit

Audited result for `as_of_date=2026-06-26`:

- evidence-backed prep audit overall_passed=true
- audit blocking reasons: none
- source gate decision: `blocked`
- source readiness score=54
- minimum owner readiness score=75
- score gap=21
- evidence_record_count=11
- strong_evidence_count=0
- audit_verified_evidence_count=0
- missing_evidence_count=11
- overall_evidence_quality=none
- remaining_gap_count=5
- blocking_gap_count=5
- evidence_ready_for_next_reevaluation_prep=false
- ready_for_controlled_gate_reevaluation=false
- eligibility_decision=not_eligible
- reevaluation_input_package_generated=true
- reevaluation_executed=false
- new_gate_score_generated=false
- new_gate_decision_generated=false
- source_gate_decision_preserved=true
- threshold_lowered=false
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- score_impact_readiness_is_not_official_score=true
- recommended next version: `v0.8.20-a-share-owner-readiness-controlled-gate-reevaluation-or-final-blocked-closeout`

Boundary:

- generates reevaluation input package but does not execute gate reevaluation
- does not generate a new formal gate score
- does not generate a new formal gate decision
- preserves source blocked decision
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat evidence-backed prep as trade instruction
- uses targeted pytest only for small version validation
- defers full pytest to `v0.9.0-or-big-version-closeout`

## v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts

v0.8.18 A-share recovery evidence collection and readiness improvement artifacts.

Adds:

- recovery evidence config
- recovery evidence input availability
- recovery evidence source resolution
- recovery evidence date alignment
- recovery task evidence collection
- developer follow-up evidence package
- owner follow-up evidence package
- quality issue evidence package
- warning mapping evidence package
- source trace improvement evidence
- markdown quality improvement evidence
- artifact completeness evidence
- readiness improvement evidence ledger
- evidence-backed score impact estimate
- evidence quality grading
- evidence gap register
- remaining blocker register
- next reevaluation prep checklist
- recovery evidence source trace
- recovery evidence boundary check
- recovery evidence manifest
- owner-facing recovery evidence reports
- recovery evidence audit

Audited result for `as_of_date=2026-06-26`:

- recovery evidence audit overall_passed=true
- audit blocking reasons: none
- source gate decision: `blocked`
- source readiness score=54
- minimum owner readiness score=75
- score gap=21
- evidence_record_count=11
- strong_evidence_count=0
- audit_verified_evidence_count=0
- missing_evidence_count=11
- overall_evidence_quality=none
- evidence_ready_for_next_reevaluation_prep=false
- actual_audited_score_changed=false
- new_audited_score=null
- new_gate_score_generated=false
- new_gate_decision_generated=false
- source_gate_decision_preserved=true
- threshold_lowered=false
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- recommended next version: `v0.8.19-a-share-owner-readiness-evidence-backed-gate-reevaluation-prep`

Boundary:

- does not fabricate evidence
- does not fabricate task completion
- does not rerun owner readiness gate
- does not generate a new gate score
- does not generate a new gate decision
- preserves source blocked decision
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat recovery evidence as trade instruction
- uses targeted pytest only for small version validation
- defers full pytest to v0.9.0 or big-version closeout

## v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation

v0.8.17 A-share owner-readiness controlled gate reevaluation.

Adds:

- controlled reevaluation config
- controlled reevaluation input availability
- controlled reevaluation source resolution
- controlled reevaluation date alignment
- reevaluation readiness guard
- reevaluation prerequisite validation
- reevaluation execution plan
- reevaluation skip decision
- not-ready reason summary
- source gate preservation check
- threshold preservation check
- waiver preservation check
- evidence sufficiency check
- controlled reevaluation decision
- controlled reevaluation source trace
- controlled reevaluation boundary check
- controlled reevaluation manifest
- controlled reevaluation summary
- owner-facing controlled reevaluation reports
- controlled gate reevaluation audit

Audited result for `as_of_date=2026-06-26`:

- controlled gate reevaluation audit overall_passed=true
- audit blocking reasons: none
- source gate decision: `blocked`
- blocked gate decision preserved=true
- readiness_guard_passed=false
- reevaluation_allowed=false
- reevaluation_skipped=true
- reevaluation_skip_reason=not_ready
- controlled_reevaluation_decision=skipped_not_ready
- evidence_sufficient_for_gate_reevaluation=false
- gate_reevaluation_executed=false
- new_gate_score_generated=false
- new_gate_decision_generated=false
- threshold_lowered=false
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- recommended next version: `v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts`

Boundary:

- records a controlled skip decision when recovery evidence is still insufficient
- does not rerun owner readiness gate
- does not change blocked gate decision
- does not generate a new gate score or new gate decision
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat controlled reevaluation as trade instruction

## v0.8.16-a-share-owner-readiness-recovery-execution-tracker-and-gate-reevaluation-prep

v0.8.16 A-share owner-readiness recovery execution tracker and gate reevaluation prep.

Adds:

- recovery execution config
- recovery execution input availability
- recovery execution source resolution
- recovery execution date alignment
- recovery task evidence registry
- recovery task status tracker
- developer follow-up evidence tracker
- owner follow-up evidence tracker
- audit-only verification evidence
- recovery task completion evaluation
- recovery evidence quality assessment
- score impact evidence assessment
- readiness improvement evidence summary
- gate reevaluation prerequisite checklist
- gate reevaluation readiness decision
- controlled reevaluation plan
- blocked state preservation check
- threshold preservation check
- waiver preservation check
- recovery execution source trace
- recovery execution boundary check
- recovery execution manifest
- owner-facing recovery execution reports
- recovery execution audit

Audited result for `as_of_date=2026-06-26`:

- recovery execution audit overall_passed=true
- audit blocking reasons: none
- source gate decision: `blocked`
- blocked gate decision preserved=true
- task_count=3
- evidence_available_count=0
- verified_by_audit_only_count=0
- completed_count=0
- tasks_marked_complete_by_default=false
- ready_for_future_gate_reevaluation=false
- gate_reevaluation_readiness_decision=not_ready
- gate_reevaluation_executed=false
- threshold_lowered=false
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- recommended next version: `v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation`

Boundary:

- tracks evidence but does not fabricate completion
- does not rerun owner readiness gate
- does not change blocked gate decision
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat recovery execution as trade instruction

## v0.8.15-a-share-owner-readiness-recovery-plan-and-quality-improvement-loop

v0.8.15 A-share owner-readiness recovery plan and quality improvement loop.

Adds:

- recovery plan config
- recovery input availability
- recovery source resolution
- recovery date alignment
- readiness gap summary
- score driver analysis
- quality exception root cause map
- quality improvement target policy
- recovery task backlog
- developer follow-up recovery plan
- owner follow-up recovery plan
- non-actionable recovery items
- recovery score impact model
- recovery milestone plan
- quality improvement loop definition
- recovery verification plan
- gate reevaluation readiness checklist
- blocked state preservation check
- recovery risk register
- recovery source trace
- recovery boundary check
- recovery manifest
- owner-facing recovery reports
- owner readiness recovery audit

Audited result for `as_of_date=2026-06-26`:

- owner readiness recovery audit overall_passed=true
- audit blocking reasons: none
- source gate decision: `blocked`
- blocked gate decision preserved=true
- minimum_owner_readiness_score=75
- actual_owner_readiness_score=54
- actual_owner_readiness_grade=D
- readiness_score_gap=21
- recovery_task_count=3
- developer_follow_up_task_count=1
- owner_follow_up_task_count=7
- ready_for_future_gate_reevaluation=false
- recovery_plan_changes_gate_decision=false
- threshold_lowered=false
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- execute_recovery_tasks=false
- recommended next version: `v0.8.16-a-share-owner-readiness-recovery-execution-tracker-and-gate-reevaluation-prep`

Boundary:

- preserves blocked gate decision
- does not lower readiness thresholds
- does not auto-waive quality gates
- does not mark recovery tasks complete by default
- does not rerun `build_from_existing_data`
- does not rerun owner readiness gate
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat recovery plan as trade instruction

## v0.8.14-a-share-owner-daily-pack-quality-exceptions-and-escalation-workflow

v0.8.14 A-share owner daily pack quality exceptions and escalation workflow.

Adds:

- quality exception workflow config
- quality exception input availability, source resolution, and date alignment
- blocked gate intake
- quality exception registry and classification
- owner readiness gap analysis
- threshold failure explanation
- waiver candidate evaluation
- manual waiver policy, request template, and decision record
- escalation workflow
- developer follow-up tracker
- owner follow-up checklist
- blocked daily pack owner notice
- exception severity matrix, routing matrix, and SLA policy
- exception audit trail
- quality exception source trace, boundary check, manifest, and summary
- owner-facing quality exception reports
- quality exception workflow audit
- CLI commands:
  - `validate-a-share-owner-quality-exceptions-inputs`
  - `build-a-share-owner-quality-exceptions`
  - `audit-a-share-owner-quality-exceptions`
  - `build-and-audit-a-share-owner-quality-exceptions`

Audited result for `as_of_date=2026-06-26`:

- owner quality exception workflow audit overall_passed=true
- audit blocking reasons: none
- source gate decision: `blocked`
- blocked gate decision preserved=true
- owner_operationally_acceptable=false
- minimum_owner_readiness_score=75
- actual_owner_readiness_score=54
- readiness_score_gap=21
- quality exceptions classified=true
- auto_waiver_allowed=false
- manual_waiver_approval_recorded=false
- waiver_changes_gate_decision=false
- no forbidden escalation routes
- no forbidden follow-up commands
- boundary clean
- recommended next version: `v0.8.15-a-share-owner-readiness-recovery-plan-and-quality-improvement-loop`

Boundary:

- preserves blocked gate decisions
- explains audit-passed-but-gate-blocked states
- does not auto-waive quality gates
- does not change the v0.8.13 gate decision
- does not rerun `build_from_existing_data`
- does not rerun owner readiness gate
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals or order previews
- does not connect broker
- does not place real orders
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat quality exceptions as trade instruction

## v0.8.13-a-share-owner-readiness-gate-and-daily-pack-quality-thresholds

v0.8.13 adds an owner-readiness gate and daily pack quality threshold layer on top of v0.8.12 owner daily pack history artifacts.

Adds:

- owner readiness gate config, input availability, source resolution, and date alignment
- owner readiness and daily pack quality threshold policies
- score, completeness, warning/issue, safe action, protected path, boundary, source trace, trend sufficiency, markdown report, artifact navigation, and owner next-step gates
- owner readiness gate decision
- quality threshold evaluation
- quality exception candidate list without automatic waiver
- owner operations release recommendation
- owner readiness gate source trace, boundary check, manifest, summary, reports, and audit
- CLI commands:
  - `validate-a-share-owner-readiness-gate-inputs`
  - `build-a-share-owner-readiness-gate`
  - `audit-a-share-owner-readiness-gate`
  - `build-and-audit-a-share-owner-readiness-gate`

Audited result for `as_of_date=2026-06-26`:

- owner readiness gate audit overall_passed=true
- audit blocking reasons: none
- gate decision: `blocked`
- owner_operationally_acceptable=false
- required_gates_passed=false
- minimum_owner_readiness_score=75
- actual_owner_readiness_score=54
- actual_owner_readiness_grade=`D`
- blocked state represented correctly because the score gate is below threshold
- source_workflow_mode=`build_from_existing_data`
- owner daily pack history audit passed
- owner daily pack audit passed
- no automatic waiver
- boundary clean
- recommended next version: `v0.8.14-a-share-owner-daily-pack-quality-exceptions-and-escalation-workflow`

Boundary:

- evaluates owner operations acceptability only
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals or order previews
- does not place orders or connect broker
- does not call old `run-daily`
- does not execute official forward dry-run day2
- does not treat owner-readiness gate as trade instruction

## v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends

v0.8.12 A-share build-output daily pack history and owner-readiness trends.

Adds:

- daily pack history config
- daily pack history input availability
- daily pack history source resolution
- daily pack history date alignment
- daily pack run record
- append-only daily pack history update
- daily pack history snapshot
- owner readiness score
- owner readiness history
- owner readiness trend sufficiency
- daily pack quality baseline
- warning issue trend baseline
- safe action trend baseline
- protected path trend baseline
- boundary trend baseline
- source trace quality trend
- daily pack completeness trend
- owner next step trend
- daily pack history source trace
- daily pack history boundary check
- daily pack history manifest and summary
- owner-facing daily pack history and readiness reports
- owner daily pack history audit
- CLI commands:
  - `validate-a-share-owner-daily-pack-history-inputs`
  - `build-a-share-owner-daily-pack-history`
  - `audit-a-share-owner-daily-pack-history`
  - `build-and-audit-a-share-owner-daily-pack-history`

Audited result for `as_of_date=2026-06-26`:

- owner daily pack history audit overall_passed=true
- blocking reasons: none
- audit warnings: none
- source_workflow_mode=`build_from_existing_data`
- owner_daily_pack_audit_passed=true
- daily_pack_history_observation_count=1
- minimum_required_observations=5
- trend_analysis_available=false
- readiness_trend_status=`insufficient_history`
- insufficient_history_correctly_flagged=true
- owner_readiness_score=54
- owner_readiness_grade=`D`
- append_only_history=true
- idempotent_append=true
- duplicate_detected=true
- same_date_changed_content_warning=false
- synthetic_history_used=false
- future_dates_used=false
- protected_path_modifications_detected=false
- automatic_action_count=0
- boundary clean
- recommended next version: `v0.8.13-a-share-owner-readiness-gate-and-daily-pack-quality-thresholds`
- validation: 1460 passed, 1 skipped

Boundary:

- uses append-only history by default
- does not fabricate historical daily packs
- does not fabricate trends
- does not rerun `build_from_existing_data`
- does not rerun owner daily pack
- does not rerun ops refresh
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not read real account data
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat owner readiness as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack

v0.8.11 A-share build-output daily runbook and owner operations decision pack.

Adds:

- daily pack config
- daily pack input availability
- daily pack source resolution
- daily pack date alignment
- owner daily status brief
- owner daily runbook
- owner operations decision pack
- owner next step checklist
- research output digest
- candidate tracking digest
- virtual portfolio digest
- warning issue digest
- safe action digest
- monitoring/remediation/ops digest
- protected path digest
- source trace digest
- boundary digest
- daily pack artifact navigation
- daily pack source trace
- daily pack boundary check
- daily pack manifest and summary
- owner-facing daily pack reports
- owner daily pack audit
- CLI commands:
  - `validate-a-share-owner-daily-pack-inputs`
  - `build-a-share-owner-daily-pack`
  - `audit-a-share-owner-daily-pack`
  - `build-and-audit-a-share-owner-daily-pack`

Audited result for `as_of_date=2026-06-26`:

- owner daily pack audit overall_passed=true
- blocking reasons: none
- audit warnings: none
- source_workflow_mode=`build_from_existing_data`
- not_investment_decision_pack=true
- build_output_ops_refresh_audit_passed=true
- build_output_dashboard_audit_passed=true
- repeatability_audit_passed=true
- gated_build_audit_passed=true
- business_output_drift_count=0
- protected_path_modifications_detected=false
- automatic_action_count=0
- execute_remediation_actions=false
- external_notifications_sent=false
- no forbidden decision categories
- no forbidden safe action types
- source trace complete and hashes match
- boundary clean
- recommended next version: `v0.8.12-a-share-build-output-daily-pack-history-and-owner-readiness-trends`
- validation: 1423 passed, 1 skipped

Boundary:

- uses build-output ops refresh as primary source
- is not an investment decision pack
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not read real account data
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat daily pack as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh

v0.8.10 A-share build-output monitoring remediation and ops refresh.

Adds:

- build output ops refresh config
- build output ops input availability
- build output ops source resolution
- build output ops date alignment
- build output monitoring refresh
- build output alert summary refresh
- build output remediation refresh
- build output safe action refresh
- build output ops center refresh
- build output ops history refresh
- build output health score refresh
- build output module status matrix refresh
- build output issue summary refresh
- build output action summary refresh
- build output owner next steps refresh
- original-ops-vs-build-output-ops comparison
- build output ops artifact navigation
- build output ops source trace
- build output ops boundary check
- build output ops manifest and summary
- owner-facing build output ops refresh reports
- build output ops refresh audit

Audited result for `as_of_date=2026-06-26`:

- build-output ops refresh audit overall_passed=true
- blocking reasons: none
- audit warnings: none
- source_workflow_mode=`build_from_existing_data`
- build_output_dashboard_audit_passed=true
- repeatability_audit_passed=true
- gated_build_audit_passed=true
- original_monitoring_audit_passed=true
- original_remediation_audit_passed=true
- original_ops_center_audit_passed=true
- monitoring_refresh_performed=true
- remediation_refresh_performed=true
- ops_center_refresh_performed=true
- ops_history_refresh_performed=true
- build_from_existing_data_rerun=false
- business_output_drift_count=0
- protected_path_modifications_detected=false
- execute_remediation_actions=false
- external_notifications_sent=false
- automatic_action_count=0
- comparison_completed=true
- ops_health_score=65
- ops_health_grade=`C`
- overall_status=`passed_with_warnings`
- boundary clean
- recommended next version: `v0.8.11-a-share-build-output-daily-runbook-and-owner-decision-pack`
- validation: 1393 passed, 1 skipped

Boundary:

- uses build-output dashboard and `build_from_existing_data` as source workflow mode
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not execute remediation actions
- does not send external notifications
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not read real account data
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat ops refresh as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh

v0.8.9 A-share current-day build output owner dashboard refresh.

Adds:

- build-output dashboard config, input availability, source resolution, and date alignment
- executive, data freshness, workflow, research output, candidate, portfolio, benchmark, performance, attribution, repeatability, protected path, warning, and blocker cards
- build-output artifact navigation
- validate-dashboard-vs-build-dashboard comparison
- build-output source trace
- build-output boundary check
- build-output dashboard manifest and summary
- owner-facing build-output dashboard, compact dashboard, artifact navigation, repeatability card, comparison report, and source trace report
- fail-close build-output owner dashboard audit
- CLI commands:
  - `validate-a-share-build-output-owner-dashboard-inputs`
  - `build-a-share-build-output-owner-dashboard`
  - `audit-a-share-build-output-owner-dashboard`
  - `build-and-audit-a-share-build-output-owner-dashboard`

Audited result for `as_of_date=2026-06-26`:

- build-output owner dashboard audit overall_passed=true
- blocking reasons: none
- audit warnings: none
- source_workflow_mode=`build_from_existing_data`
- repeatability_audit_passed=true
- gated_build_audit_passed=true
- validate_source_dashboard_audit_passed=true
- data_refresh_audit_passed=true
- required_cards_present=true
- optional_cards_present=true
- business_output_drift_count=0
- protected_path_modifications_detected=false
- required_validate_fallback_used=false
- optional_validate_fallback_used=false
- comparison_completed=true
- boundary clean
- recommended next version: `v0.8.10-a-share-build-output-monitoring-remediation-and-ops-refresh`
- validation: 1372 passed, 1 skipped

Boundary:

- refreshes dashboard artifacts from stable `build_from_existing_data` output
- prefers build output over validate-source artifacts
- requires repeatability audit success and zero business output drift
- distinguishes pre-existing protected paths from modified protected paths
- does not rerun `build_from_existing_data`
- does not refresh public network data
- does not run `full_research_run`
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not read real account data
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat dashboard output as a trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability

v0.8.8 A-share build_from_existing_data repeatability and diff stability.

Adds:

- repeatability config
- repeatability input availability
- repeatability date alignment
- protected path pre-run snapshot
- repeat build execution plan
- repeat build execution record
- repeat build workflow result
- protected path post-run snapshot
- protected path modification check
- first and second build artifact snapshots
- build-vs-build comparison
- repeatability drift summary
- deterministic field normalization
- repeatability warning comparison
- repeatability source trace
- repeatability boundary check
- repeatability manifest and summary
- owner-facing repeatability reports
- build repeatability audit

Audited result for `as_of_date=2026-06-26`:

- repeatability audit overall_passed=true
- blocking reasons: none
- audit warnings: none
- workflow_mode=`build_from_existing_data`
- repeat_build_execution_performed=true
- repeat_build_audit_passed=true
- comparison_completed=true
- business_output_drift_count=0
- timestamp_only_drift_count=41
- metadata_hash_drift_count=23
- missing_required_artifact_count=0
- boundary_drift=false
- protected_path_drift=false
- source_trace_missing=false
- preexisting protected paths: `data/orders`, `data/trades`
- protected_path_modifications_detected=false
- protected files modified/created/deleted: none
- recommended next version: `v0.8.9-a-share-current-day-build-output-owner-dashboard-refresh`
- validation: 1350 passed, 1 skipped

Boundary:

- repeats gated `build_from_existing_data`
- distinguishes pre-existing protected paths from modified protected paths
- does not refresh public network data
- does not run `full_research_run`
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not read real account data
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat repeatability as a trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.7-a-share-gated-current-day-build-from-existing-data-dry-run

v0.8.7 A-share gated current-day build-from-existing-data dry-run.

Adds:

- gated build-from-existing-data config, preflight gate, execution plan, execution record, workflow result, audit link, artifact index, validate-vs-build comparison, artifact drift summary, warning summary, source trace, boundary check, manifest, summary, and owner-facing reports
- CLI commands:
  - `validate-a-share-gated-build-inputs`
  - `build-a-share-gated-build-from-existing-data`
  - `audit-a-share-gated-build-from-existing-data`
  - `build-and-audit-a-share-gated-build-from-existing-data`
- audit docs and schema/runbook docs for the gated build evidence package
- workflow audit compatibility for `build_from_existing_data` when existing downstream artifacts are present

Audited result for `as_of_date=2026-06-26`:

- gated build audit overall_passed=true
- blocking reasons: none
- audit warnings: none
- preflight_gate_passed=true
- ops_history_audit_passed=true
- ops_center_audit_passed=true
- current_day_audit_passed=true
- data_refresh_audit_passed=true
- gated_build_execution_performed=true
- workflow_mode=`build_from_existing_data`
- workflow_audit_passed=true
- comparison_completed=true
- missing_required_artifacts=[]
- boundary_drift=false
- source_trace_missing=false
- source_trace_hashes_match=true
- recommended next version: `v0.8.8-a-share-build-from-existing-data-repeatability-and-diff-stability`
- validation: 1324 passed, 1 skipped

Boundary:

- executes only the gated current-day `build_from_existing_data` dry-run
- does not run public network refresh
- does not run `full_research_run`
- does not call old run-daily
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate order preview
- does not generate buy/sell signals
- does not execute official forward dry-run day2
- does not send external notifications
- does not treat build output as a trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines

v0.8.6 A-share ops run history deepening and trend baselines.

Adds:

- ops history config
- ops history input availability
- ops run record
- append-only ops run history index
- ops history snapshot
- trend baseline config
- trend sufficiency evaluation
- health score history and baseline
- module reliability baseline
- warning, issue, and safe action recurrence baselines
- boundary history snapshot
- baseline drift snapshot
- ops history source trace
- ops history boundary check
- ops history manifest and summary
- owner-facing ops history Markdown reports
- fail-close ops history audit

Audited result for `as_of_date=2026-06-26`:

- ops history audit overall_passed=true
- blocking reasons: none
- warnings: none
- run_history_observation_count=1
- minimum_required_observations=5
- trend_analysis_available=false
- baseline_status=insufficient_history
- synthetic_history_used=false
- future_dates_used=false
- append_completed=true
- idempotent_append=true
- duplicate_detected=true
- records_before=1
- records_after=1
- commands_executed=[]
- source trace complete
- boundary clean
- recommended next version: `v0.8.7-a-share-current-day-build-from-existing-data-promotion-gate`
- validation: 1303 passed, 1 skipped

Boundary:

- appends real ops run history only
- does not synthesize historical observations
- does not use future dates
- does not refresh data
- does not rerun current-day research
- does not rebuild dashboard, monitoring, remediation, or ops center artifacts
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat trend baselines as trade instructions
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.5-a-share-daily-ops-command-center

v0.8.5 A-share daily ops command center.

Adds:

- ops center config
- ops input availability
- ops date alignment
- ops plan
- ops execution record
- ops health score card
- ops module status matrix
- ops issue summary
- ops action summary
- ops artifact navigation
- ops command reference
- ops owner next steps
- ops source trace
- ops boundary check
- ops manifest
- owner-facing ops command center report
- compact ops report
- ops audit

Audited result for `as_of_date=2026-06-26`:

- ops audit overall_passed=true
- blocking reasons: none
- warnings: none
- ops health score: 65
- ops health grade: C
- overall_status=passed_with_warnings
- required_modules_available=true
- dates_aligned=true
- input data refresh/current-day/dashboard/monitoring/remediation audits passed
- blocking_issue_count=0
- warning_issue_count=10
- known_non_blocking_issue_count=5
- safe_action_count=8
- automatic_action_count=0
- commands_executed=[]
- aggregate_existing_artifacts_only=true
- external_notifications_sent=false
- source trace complete
- boundary clean
- recommended next version: `v0.8.6-a-share-ops-run-history-deepening-and-trend-baselines`
- validation: 1281 passed, 1 skipped

Boundary:

- aggregates existing ops artifacts by default
- does not refresh data by default
- does not rerun current-day research by default
- does not execute remediation actions
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat ops output as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.4-a-share-owner-remediation-runbook-and-action-checklist

v0.8.4 A-share owner remediation runbook and action checklist.

Adds:

- remediation config
- remediation input availability
- issue catalog
- warning remediation map
- blocking remediation map
- alert remediation map
- provider remediation guide
- data freshness remediation guide
- schema coverage remediation guide
- workflow remediation guide
- dashboard remediation guide
- monitoring remediation guide
- safe owner action checklist
- manual verification checklist
- non-actionable issue list
- dry-run remediation plan
- remediation priority summary
- remediation source trace
- remediation boundary check
- remediation manifest
- owner remediation reports
- owner remediation audit

Audited result for `as_of_date=2026-06-26`:

- remediation audit overall_passed=true
- blocking reasons: none
- warnings: none
- issue_count=17
- blocking_issue_count=0
- warning_issue_count=10
- known_non_blocking_issue_count=5
- safe_action_count=8
- automatic_action_count=0
- commands_executed=[]
- execute_remediation_actions=false
- external_notifications_sent=false
- input owner monitoring audit passed
- input owner dashboard audit passed
- input current-day run audit passed
- input data refresh audit passed
- source trace complete
- boundary clean
- recommended next version: `v0.8.5-a-share-daily-ops-command-center`
- validation: 1259 passed, 1 skipped

Boundary:

- generates runbooks and checklists only
- does not execute remediation actions
- does not refresh data
- does not rerun research workflow
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat remediation as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.3-a-share-owner-alerting-and-run-history-monitoring

This release adds local owner alerting and run history monitoring for the A-share research system.

Includes:

- monitoring config
- monitoring input availability
- run history update
- run history snapshot
- append-only run history index
- warning history index
- blocking history index
- alert history index
- alert rule config
- alert evaluation result
- alert event log
- warning trend snapshot
- blocking trend snapshot
- provider health trend snapshot
- workflow health trend snapshot
- dashboard health trend snapshot
- monitoring status card
- owner alert summary card
- run history summary card
- monitoring source trace
- monitoring boundary check
- monitoring manifest
- monitoring summary
- owner monitoring Markdown reports
- owner monitoring fail-close audit
- CLI commands: `validate-a-share-owner-monitoring-inputs`, `build-a-share-owner-monitoring`, `audit-a-share-owner-monitoring`, and `build-and-audit-a-share-owner-monitoring`

Audited result for `as_of_date=2026-06-26`:

- owner monitoring audit overall_passed=true
- blocking reasons: none
- warnings: none
- run_history_observation_count=1
- trend_analysis_available=false
- insufficient_history_correctly_flagged=true
- critical alerts: 0
- warning alerts: 0
- informational alerts: 0
- known non-blocking alerts: 0
- external_notifications_sent=false
- input owner dashboard audit passed
- input current-day run audit passed
- input data refresh audit passed
- source trace complete
- boundary check passed
- recommended next version: `v0.8.4-a-share-owner-remediation-runbook-and-action-checklist`
- validation: 1233 passed, 1 skipped

Boundary:

- generates local alert artifacts only
- does not send external notifications by default
- does not refresh data
- does not rerun the research workflow
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate buy/sell signals
- does not generate order preview
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat alerts as trade instructions
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard

This release adds a research-only owner dashboard for the existing A-share current-day research run.

Includes:

- owner dashboard config and input availability validation
- executive, data freshness, provider health, workflow, research output, candidate, portfolio, benchmark, performance, attribution, warning/blocker, artifact navigation, source trace, boundary, manifest, and summary JSON artifacts
- owner-facing Markdown dashboard, compact dashboard, warning/blocker summary, artifact navigation, and source trace reports
- owner dashboard fail-close audit
- CLI commands: `validate-a-share-owner-dashboard-inputs`, `build-a-share-owner-dashboard`, `audit-a-share-owner-dashboard`, and `build-and-audit-a-share-owner-dashboard`

Audited result for `as_of_date=2026-06-26`:

- owner dashboard audit overall_passed=true
- blocking reasons: none
- warnings: 11
- mode tested: `build_dashboard_from_existing_run`
- resolved_as_of_date: `2026-06-26`
- required cards present
- optional cards present
- source trace complete
- boundary check passed
- no forbidden artifacts generated
- no forbidden positive wording found
- recommended next version: `v0.8.3-a-share-owner-alerting-and-run-history-monitoring`
- validation: owner dashboard focused tests 20 passed

Boundary:

- does not refresh data
- does not rerun the research workflow
- does not connect broker
- does not read real account data
- does not place real orders
- does not generate buy/sell signals
- does not generate order preview
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat dashboard content as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.1-a-share-current-day-research-workflow-runner

This release adds a research-only A-share current-day research workflow runner.

Includes:

- current-day run config
- current-day readiness check
- data refresh link
- workflow plan
- workflow execution record
- current-day stage manifest
- artifact index
- warning summary
- current-day source trace
- current-day boundary check
- current-day run manifest
- current-day owner summary
- current-day research run audit
- CLI commands: `validate-a-share-current-day-readiness`, `run-a-share-current-day-research`, `audit-a-share-current-day-research-run`, and `run-and-audit-a-share-current-day-research`

Audited result for `as_of_date=2026-06-26`:

- current-day research run audit overall_passed=true
- blocking reasons: none
- warnings: 9
- mode tested: `run_research_from_existing_refresh`
- workflow_mode tested: `validate_existing_artifacts`
- resolved_as_of_date: `2026-06-26`
- data refresh audit passed
- critical datasets passed
- schema validation passed
- freshness validation passed
- coverage validation passed
- known data refresh warnings carried forward
- workflow audit passed
- workflow command uses the new A-share daily research workflow CLI
- old run-daily called=false
- recommended next version: `v0.8.2-a-share-current-day-owner-briefing-and-monitoring-dashboard`
- validation: 1194 passed, 1 skipped

Boundary:

- does not connect broker
- does not read real account data
- does not place real orders
- does not generate buy/sell signals
- does not generate order preview
- does not call old run-daily
- does not execute official forward dry-run day2
- does not treat research output as trade instruction
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.8.0-a-share-daily-data-refresh-and-provider-hardening

This release adds research-only A-share daily data refresh validation and provider hardening.

Includes:

- daily data refresh configuration
- latest completed trading day date resolution
- provider registry snapshot
- provider health check
- provider execution log
- dataset contracts
- dataset refresh plan
- dataset refresh result
- schema validation
- freshness validation
- coverage summary
- data gap report
- provider fallback report
- data refresh source trace
- data refresh manifest
- data refresh boundary check
- owner-facing refresh reports
- data refresh audit
- CLI commands: `build-a-share-daily-data-refresh`, `audit-a-share-daily-data-refresh`, and `build-and-audit-a-share-daily-data-refresh`

Audited result for `as_of_date=2026-06-26`:

- data refresh audit overall_passed=true
- blocking reasons: none
- warnings: 2 (`daily_basic:required_field_all_null`, `trading_calendar:exchange_level_calendar_collapsed_to_trade_date`)
- mode tested: `validate_existing_data`
- resolved_as_of_date: `2026-06-26`
- datasets checked: equity_master, daily_price, adjusted_price, daily_basic, index_price, industry_classification, financial_indicators, trading_calendar
- schema validation passed
- freshness validation passed
- coverage validation passed
- critical datasets available
- provider fallback used=false
- network providers used=false
- broker provider used=false
- real account provider used=false
- order provider used=false
- recommended next version: `v0.8.1-a-share-current-day-research-workflow-runner`
- validation: 1174 passed, 1 skipped

Boundary:

- does not trigger the full research workflow by default
- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not use real-account provider
- does not use order provider
- does not place real orders
- does not call old run-daily
- does not execute official forward dry-run day2
- does not claim model profit guarantee
- does not claim live trading readiness

## v0.7.12-a-share-performance-attribution-and-risk-diagnostics

This release adds research-only A-share virtual portfolio performance attribution and risk diagnostics.

Includes:

- attribution config
- attribution data availability
- holding contribution snapshot
- industry contribution snapshot
- candidate source contribution snapshot
- score bucket contribution snapshot
- risk bucket contribution snapshot
- liquidity bucket contribution snapshot
- benchmark relative attribution snapshot
- portfolio concentration diagnostics
- risk diagnostics
- liquidity diagnostics
- industry diagnostics
- factor exposure snapshot
- attribution limitations
- attribution source trace
- attribution boundary check
- attribution audit
- CLI commands: `build-a-share-performance-attribution`, `audit-a-share-performance-attribution`, and `build-and-audit-a-share-performance-attribution`

Audited result for `as_of_date=2026-06-26`:

- attribution audit overall_passed=true
- blocking reasons: none
- warnings: 1 limited-history warning
- mode tested: `current_exposure_diagnostics`
- current release correctly flags limited performance history
- structural diagnostics are available
- realized performance attribution is not fabricated
- `risk_downgraded_symbols_in_portfolio=[]`
- `excluded_universe_exposure=0`
- holding, industry, score bucket, risk bucket, and liquidity bucket weights reconcile
- recommended next version: `v0.8.0-a-share-daily-data-refresh-and-provider-hardening`
- validation: 1154 passed, 1 skipped

Boundary:

- does not generate buy/sell signals
- does not generate order preview
- does not connect broker
- does not place real orders
- does not call old run-daily
- does not execute official forward dry-run day2
- does not fabricate performance
- does not claim model profit guarantee
- does not claim live trading readiness
- attribution is not used as a trade signal

## v0.7.11-a-share-multi-day-portfolio-performance-tracking

This release adds research-only multi-day virtual portfolio performance tracking for A-share long/mid/short virtual portfolios.

Includes:

- performance config
- performance data availability
- portfolio NAV series
- portfolio return series
- portfolio drawdown series
- benchmark-relative performance series
- holding mark-to-market series
- performance metric snapshot
- performance limitations report
- append-only performance log
- performance source trace
- performance boundary check
- performance audit
- CLI commands: `build-a-share-multi-day-performance`, `audit-a-share-multi-day-performance`, and `build-and-audit-a-share-multi-day-performance`
- `current_snapshot` mode
- `append_from_existing_tracking` mode
- `rebuild_virtual_performance_series` mode with explicit safeguards

Audited result for `as_of_date=2026-06-26`:

- performance audit overall_passed=true
- blocking reasons: none
- portfolio observation counts: long=1, mid=1, short=1
- minimum required observations: 20
- sufficient_history=false
- insufficient_history correctly flagged
- first_day_initialization=true
- performance_not_yet_observed=true
- current release correctly flags limited history and first-day initialization
- does not fabricate multi-day performance
- recommended next version: `v0.7.12-a-share-performance-attribution-and-risk-diagnostics`
- validation: 1131 passed, 1 skipped

Boundary:

- research-only and virtual-only
- no buy/sell signals generated
- no order preview generated
- no broker connected
- no real orders placed
- old run-daily not called
- official forward dry-run day2 not executed
- not model profit guarantee
- not live trading ready

## v0.7.10-a-share-benchmark-data-and-performance-comparison

This release adds research-only A-share benchmark data and performance comparison for the existing long/mid/short virtual portfolios.

Includes:

- CSI300, CSI500, and CSI1000 benchmark support using local/public historical index data
- CASH benchmark with zero daily return
- equal-weight strict tradable benchmark
- equal-weight candidate pool benchmark
- benchmark NAV and return snapshots
- portfolio benchmark comparison
- relative performance snapshot
- benchmark source trace
- benchmark boundary check
- benchmark audit
- CLI commands: `build-a-share-benchmark-comparison`, `audit-a-share-benchmark-comparison`, and `build-and-audit-a-share-benchmark-comparison`

Audited result for `as_of_date=2026-06-26`:

- benchmark audit overall_passed=true
- blocking reasons: none
- benchmark ids available: CSI300, CSI500, CSI1000, CASH, EQUAL_WEIGHT_STRICT_TRADABLE, EQUAL_WEIGHT_CANDIDATE_POOL
- placeholder benchmarks used: none
- limited first-day portfolio history explicitly flagged
- performance_not_yet_observed=true
- recommended next version: `v0.7.11-a-share-multi-day-portfolio-performance-tracking`

Boundary:

- benchmark comparison is research-only
- no buy/sell signals generated
- no order preview generated
- no broker connected
- no real orders placed
- old run-daily not called
- official forward dry-run day2 not executed
- not model profit guarantee
- not live trading ready

## v0.7.9-a-share-daily-workflow-orchestration

This release adds the A-share daily research workflow orchestration layer. It strings the existing v0.7.2-v0.7.8 research chain into a repeatable, auditable, fail-closed daily workflow without rewriting upstream business modules.

Includes:

- fixed root import shim version mismatch
- workflow config
- workflow preflight
- workflow stage manifest
- workflow run manifest
- workflow source trace
- workflow boundary check
- owner-facing Chinese workflow summary
- workflow audit
- `validate_existing_artifacts` mode
- `build_from_existing_data` mode
- `full_research_run` mode with public data refresh disabled by default
- CLI commands: `preflight-a-share-daily-workflow`, `run-a-share-daily-research-workflow`, `audit-a-share-daily-research-workflow`, and `run-and-audit-a-share-daily-research-workflow`

Audited result for `as_of_date=2026-06-26` in `validate_existing_artifacts` mode:

- workflow audit overall_passed=true
- blocking reasons: none
- warnings: 7, all inherited from known upstream evidence/placeholder warnings
- stage counts: total=11, passed=11, failed=0, skipped=0, blocked=0, not_run=0
- candidate counts: long=30, mid=30, short=30, extended=300
- portfolio NAVs: long=1000000.0, mid=1000000.0, short=1000000.0
- source trace complete=true
- upstream audits passed=true
- build_timestamp_non_strict_idempotency=true
- benchmark placeholder deferred to v0.7.10
- recommended next version: `v0.7.10-a-share-benchmark-data-and-performance-comparison`

Boundary:

- workflow orchestration only
- does not rewrite upstream business modules
- old run-daily not called
- official forward dry-run status unchanged
- day2 not executed
- no broker connected
- no real orders placed
- no buy/sell signals generated
- no order preview generated
- not model profit guarantee
- not live trading ready

Validation: 1092 tests passed, 1 skipped.

## v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger

This release adds research-only A-share virtual portfolio tracking and paper ledgers on top of the v0.7.6 long/mid/short virtual portfolios and the v0.7.7 daily briefing. It builds virtual initial positions, holdings snapshots, NAV, first-day performance, drawdown, exposure, benchmark comparison placeholders, source trace, reports, and a fail-closed audit.

Includes:

- virtual portfolio tracking config
- long/mid/short paper ledgers
- long/mid/short holdings snapshots
- NAV snapshot
- performance snapshot
- drawdown snapshot
- exposure snapshot
- benchmark comparison snapshot
- tracking manifest and source trace
- virtual portfolio tracking audit
- CLI commands: `build-a-share-virtual-portfolio-tracking`, `audit-a-share-virtual-portfolio-tracking`, and `build-and-audit-a-share-virtual-portfolio-tracking`

Audited result for `as_of_date=2026-06-26`:

- tracking audit overall_passed=true
- blocking reasons: none
- warnings: 1, CSI300/CSI500/CSI1000 benchmark price series unavailable and preserved as placeholders
- long holdings / ledger records: 30 / 30
- mid holdings / ledger records: 30 / 30
- short holdings / ledger records: 20 / 20
- long NAV / weight sum: 1000000.0 / 1.0
- mid NAV / weight sum: 1000000.0 / 1.0
- short NAV / weight sum: 1000000.0 / 1.0
- first_day_initialization=true
- performance_not_yet_observed=true
- paper_ledger_generated=true
- real_portfolio_generated=false
- buy_sell_signals_generated=false
- order_preview_generated=false
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- not model profit guarantee
- recommended next version: `v0.7.9-a-share-daily-workflow-orchestration`

Primary artifacts:

- `data/equity_portfolio_tracking/daily/2026-06-26/tracking_config.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/long_paper_ledger.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/mid_paper_ledger.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/short_paper_ledger.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/long_holdings_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/mid_holdings_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/short_holdings_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/portfolio_nav_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/portfolio_performance_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/portfolio_drawdown_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/portfolio_exposure_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/benchmark_comparison_snapshot.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/tracking_manifest.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/tracking_source_trace.json`
- `data/equity_portfolio_tracking/daily/2026-06-26/tracking_summary.json`
- `outputs/equity_portfolio_tracking/daily/2026-06-26/VIRTUAL_PORTFOLIO_TRACKING_SUMMARY.md`
- `outputs/equity_portfolio_tracking/daily/2026-06-26/LONG_PORTFOLIO_TRACKING.md`
- `outputs/equity_portfolio_tracking/daily/2026-06-26/MID_PORTFOLIO_TRACKING.md`
- `outputs/equity_portfolio_tracking/daily/2026-06-26/SHORT_PORTFOLIO_TRACKING.md`
- `outputs/equity_portfolio_tracking/daily/2026-06-26/BENCHMARK_COMPARISON.md`
- `data/equity_data_quality/a_share_virtual_portfolio_tracking_audit.json`
- `outputs/audit/A_SHARE_VIRTUAL_PORTFOLIO_TRACKING_AUDIT.md`

Boundary:

- paper ledger is virtual-only and research-only
- paper ledger is not a real-money ledger
- virtual holdings are not real holdings
- virtual returns are not actual returns
- no real portfolio generated
- no buy/sell signals generated
- no order preview generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- not a model profit guarantee
- live trading readiness remains false
- v0.7.9 implements the workflow orchestration handoff; v0.7.10 is the next benchmark data and performance comparison stage

Validation: 1075 tests passed, 1 skipped.

## v0.7.7-a-share-daily-stock-selection-briefing

This release adds the daily Chinese A-share stock selection research briefing on top of the v0.7.6 virtual portfolio package. The briefing reads existing feature, score, candidate, virtual portfolio, exposure, risk/liquidity, and audit artifacts only. It does not regenerate scores, candidates, or virtual portfolios. It does not generate buy/sell signals, order previews, broker artifacts, real orders, profit guarantees, or live-trading readiness claims.

Includes:

- daily stock selection briefing JSON
- daily stock selection briefing Markdown report
- briefing source trace JSON and Markdown
- briefing manifest
- briefing boundary check
- briefing audit
- long/mid/short candidate Top 10 summaries
- multi-horizon candidate summary
- risk-downgraded candidate summary
- long/mid/short virtual portfolio summaries
- industry exposure and concentration summary
- risk/liquidity summary
- CLI commands: `build-a-share-daily-stock-selection-briefing`, `audit-a-share-daily-stock-selection-briefing`, and `build-and-audit-a-share-daily-stock-selection-briefing`

Audited result for `as_of_date=2026-06-26`:

- briefing audit overall_passed=true
- blocking reasons: none
- warnings: 5, including partial fundamental score confidence and documented `Unclassified` industry fallback disclosures
- required sections: all present
- long candidates Top 10 included
- mid candidates Top 10 included
- short candidates Top 10 included
- multi-horizon section included
- risk-downgraded section included
- virtual portfolio section included
- industry exposure section included
- risk/liquidity section included
- do-not-misread section included
- source trace complete=true
- recommended next version: `v0.7.8-a-share-virtual-portfolio-tracking-and-paper-ledger`

Primary artifacts:

- `data/equity_briefings/daily/2026-06-26/daily_stock_selection_briefing.json`
- `data/equity_briefings/daily/2026-06-26/briefing_manifest.json`
- `data/equity_briefings/daily/2026-06-26/briefing_source_trace.json`
- `data/equity_briefings/daily/2026-06-26/briefing_boundary_check.json`
- `outputs/equity_briefings/daily/2026-06-26/DAILY_STOCK_SELECTION_BRIEFING.md`
- `outputs/equity_briefings/daily/2026-06-26/BRIEFING_SOURCE_TRACE.md`
- `data/equity_data_quality/a_share_daily_stock_selection_briefing_audit.json`
- `outputs/audit/A_SHARE_DAILY_STOCK_SELECTION_BRIEFING_AUDIT.md`

Boundary:

- briefing only
- existing artifacts read only
- no scores regenerated
- no candidates regenerated
- no virtual portfolios regenerated
- no buy/sell signals generated
- no order preview generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- not a model profit guarantee
- live trading readiness remains false

Validation: 1056 tests passed, 1 skipped.

## v0.7.6-a-share-virtual-portfolio-construction

This release adds A-share research-only virtual portfolio construction on top of the v0.7.5 candidate package. It generates long, mid, and short virtual portfolios, target weights, industry exposure, risk/liquidity summaries, a manifest, reports, and a fail-closed audit. Virtual portfolios are not real portfolios. Virtual target weights are not order instructions, not broker order previews, not buy/sell signals, and not profit guarantees.

Includes:

- long virtual portfolio
- mid virtual portfolio
- short virtual portfolio
- portfolio construction config
- portfolio target weights
- industry exposure summary
- risk/liquidity summary
- portfolio manifest
- virtual portfolio construction audit
- CLI commands: `build-a-share-virtual-portfolios`, `audit-a-share-virtual-portfolios`, and `build-and-audit-a-share-virtual-portfolios`

Audited result for `as_of_date=2026-06-26`:

- long holdings: 30
- mid holdings: 30
- short holdings: 20
- long weight sum: 1.0
- mid weight sum: 1.0
- short weight sum: 1.0
- long max single weight: 0.037139
- mid max single weight: 0.036981
- short max single weight: 0.055804
- long max industry weight: 0.25
- mid max industry weight: 0.25
- short max industry weight: 0.30
- audit overall_passed=true
- blocking reasons: none
- warnings: 3, raw `industry_level_1` contains `Unclassified`; audit uses documented fallback industry buckets for caps
- risk-downgraded symbols included: none
- excluded-universe symbols included: none
- recommended next version: `v0.7.7-a-share-daily-stock-selection-briefing`

Primary artifacts:

- `data/equity_portfolios/daily/2026-06-26/portfolio_construction_config.json`
- `data/equity_portfolios/daily/2026-06-26/long_virtual_portfolio.json`
- `data/equity_portfolios/daily/2026-06-26/long_virtual_portfolio.parquet`
- `data/equity_portfolios/daily/2026-06-26/mid_virtual_portfolio.json`
- `data/equity_portfolios/daily/2026-06-26/mid_virtual_portfolio.parquet`
- `data/equity_portfolios/daily/2026-06-26/short_virtual_portfolio.json`
- `data/equity_portfolios/daily/2026-06-26/short_virtual_portfolio.parquet`
- `data/equity_portfolios/daily/2026-06-26/portfolio_weight_summary.json`
- `data/equity_portfolios/daily/2026-06-26/portfolio_industry_exposure.json`
- `data/equity_portfolios/daily/2026-06-26/portfolio_risk_liquidity_summary.json`
- `data/equity_portfolios/daily/2026-06-26/portfolio_manifest.json`
- `data/equity_data_quality/a_share_virtual_portfolio_construction_audit.json`
- `outputs/equity_portfolios/daily/2026-06-26/PORTFOLIO_CONSTRUCTION_SUMMARY.md`
- `outputs/audit/A_SHARE_VIRTUAL_PORTFOLIO_CONSTRUCTION_AUDIT.md`

Boundary:

- virtual portfolio construction only
- virtual portfolios generated from candidate pools
- no real portfolio generated
- no buy/sell signals generated
- no order preview generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- not a model profit guarantee
- live trading readiness remains false

Validation: 1046 tests passed, 1 skipped.

## v0.7.5-a-share-candidate-generation-system

This release adds the A-share candidate generation system on top of the v0.7.4 strict-universe score package. It generates long, mid, and short research candidate pools, an extended watch pool, multi-horizon overlap candidates, risk-downgraded candidates, explanations, risk notes, a manifest, reports, and a fail-closed candidate audit. Candidates are research inputs only. They are not investment advice, not buy/sell signals, not order instructions, not virtual portfolios, and not a profit guarantee.

Includes:

- long candidate generation
- mid candidate generation
- short candidate generation
- extended watch pool
- multi-horizon candidates
- risk-downgraded candidates
- candidate reason taxonomy
- candidate explanations and risk notes
- candidate generation manifest
- candidate generation audit
- CLI commands: `generate-a-share-candidates`, `audit-a-share-candidates`, and `generate-and-audit-a-share-candidates`

Audited result for `as_of_date=2026-06-26`:

- strict tradable count: 3676
- scored symbols: 3676
- long candidates: 30
- mid candidates: 30
- short candidates: 30
- extended watch pool: 300
- multi-horizon candidates: 50
- risk-downgraded candidates: 294
- audit overall_passed=true
- blocking reasons: none
- warnings: 0
- candidate artifacts generated: true
- watchlists generated: true
- virtual portfolio artifacts present: none
- buy/sell signal artifacts present: none
- order preview artifacts present: none
- recommended next version: `v0.7.6-a-share-virtual-portfolio-construction`

Primary artifacts:

- `data/equity_selection/daily/2026-06-26/candidate_generation_config.json`
- `data/equity_selection/daily/2026-06-26/long_candidates.json`
- `data/equity_selection/daily/2026-06-26/long_candidates.parquet`
- `data/equity_selection/daily/2026-06-26/mid_candidates.json`
- `data/equity_selection/daily/2026-06-26/mid_candidates.parquet`
- `data/equity_selection/daily/2026-06-26/short_candidates.json`
- `data/equity_selection/daily/2026-06-26/short_candidates.parquet`
- `data/equity_selection/daily/2026-06-26/extended_watch_pool.json`
- `data/equity_selection/daily/2026-06-26/extended_watch_pool.parquet`
- `data/equity_selection/daily/2026-06-26/multi_horizon_candidates.json`
- `data/equity_selection/daily/2026-06-26/risk_downgraded_candidates.json`
- `data/equity_selection/daily/2026-06-26/candidate_reason_breakdown.json`
- `data/equity_selection/daily/2026-06-26/candidate_generation_summary.json`
- `data/equity_selection/daily/2026-06-26/candidate_manifest.json`
- `data/equity_data_quality/a_share_candidate_generation_audit.json`
- `outputs/equity_selection/daily/2026-06-26/CANDIDATE_GENERATION_SUMMARY.md`
- `outputs/audit/A_SHARE_CANDIDATE_GENERATION_AUDIT.md`

Boundary:

- candidate generation only
- candidates generated from score tables and strict tradable universe
- extended watch pool generated as research input only
- no virtual portfolios generated
- no buy/sell signals generated
- no order preview generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- not a model profit guarantee
- live trading readiness remains false

Validation: 1031 tests passed, 1 skipped.

## v0.7.4-a-share-long-mid-short-scoring-system

This release adds the A-share long/mid/short scoring system on top of the v0.7.3 strict-universe feature package. It generates scores, ranks, percentiles, distributions, component breakdowns, reports, and an audit for the strict tradable universe only. Scores are not recommendations, not buy/sell signals, not candidate pools, not watchlists, not virtual portfolios, and not profit or live-trading claims.

Includes:

- versioned score config and cross-sectional normalization with 1% / 99% winsorization
- `RiskScore`
- `LiquidityScore`
- `IndustryScore`
- `FundamentalScore`
- `LongScore`
- `MidScore`
- `ShortScore`
- `CompositeOpportunityScore`
- score component breakdown
- score distribution report
- scoring audit
- CLI commands: `build-a-share-scores`, `audit-a-share-scores`, and `build-and-audit-a-share-scores`

Audited result for `as_of_date=2026-06-26`:

- strict tradable count: 3676
- scored symbols: 3676
- long / mid / short / composite score symbols: 3676 each
- LongScore range: 28.067582 to 70.446463
- MidScore range: 16.933246 to 85.477234
- ShortScore range: 17.027915 to 83.987027
- RiskScore range: 2.343807 to 97.451374
- LiquidityScore range: 16.168843 to 85.406692
- IndustryScore range: 17.826589 to 86.121588
- FundamentalScore range: 29.313306 to 73.700185
- CompositeOpportunityScore range: 23.917386 to 76.936048
- audit overall_passed=true
- blocking reasons: none
- warnings: 1, fundamental score confidence is partial
- candidate artifacts present: none
- watchlist artifacts present: none
- virtual portfolio artifacts present: none
- recommended next version: `v0.7.5-a-share-candidate-generation-system`

Primary artifacts:

- `data/equity_scores/daily/2026-06-26/score_config.json`
- `data/equity_scores/daily/2026-06-26/risk_liquidity_industry_fundamental_scores.parquet`
- `data/equity_scores/daily/2026-06-26/horizon_scores.parquet`
- `data/equity_scores/daily/2026-06-26/composite_scores.parquet`
- `data/equity_scores/daily/2026-06-26/score_component_breakdown.parquet`
- `data/equity_scores/daily/2026-06-26/score_distribution.json`
- `data/equity_scores/daily/2026-06-26/score_manifest.json`
- `data/equity_scores/daily/2026-06-26/scoring_summary.json`
- `data/equity_data_quality/a_share_scoring_audit.json`
- `outputs/equity_scores/daily/2026-06-26/SCORE_DISTRIBUTION_REPORT.md`
- `outputs/equity_scores/daily/2026-06-26/SCORING_SUMMARY.md`
- `outputs/audit/A_SHARE_SCORING_AUDIT.md`

Boundary:

- scoring only
- scores generated for strict tradable universe only
- no candidate stocks generated
- no watchlists generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- not a model profit guarantee
- live trading readiness remains false

Validation: 1017 tests passed, 1 skipped.

## v0.7.3-a-share-multi-horizon-feature-engineering

This release adds the A-share multi-horizon feature engineering layer on top of the v0.7.2 strict tradable universe. It generates feature tables only. It does not generate LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, candidates, watchlists, virtual portfolios, broker instructions, real orders, `run-daily` output, profit claims, or live-trading readiness.

Includes:

- strict-universe feature input loader with exact `as_of_date` fail-closed behavior
- explicit `--allow-latest-tradable-universe` escape hatch for non-default historical runs
- short-horizon price, momentum, volume, gap, range, and breakout features
- mid-horizon moving average, trend, relative strength, and volatility-adjusted return features
- long-horizon 250d/3y/5y trend, drawdown, annualized return, volatility, and relative strength features
- risk features including volatility, downside volatility, drawdown, VaR, expected shortfall, skew/kurtosis, limit/drop/gap counts
- liquidity features including amount, volume, turnover, stability, effective-day, zero-volume, and slippage-proxy fields
- industry features including industry return, relative strength, member count, and allowed in-industry return rank features
- fundamental features from daily basic and financial history with nullable valuation percentile placeholders
- feature manifest, field coverage, generation summary, Markdown reports, and fail-closed audit
- CLI commands: `build-a-share-multi-horizon-features`, `audit-a-share-multi-horizon-features`, and `build-and-audit-a-share-multi-horizon-features`

Audited result for `as_of_date=2026-06-26`:

- strict tradable count: 3676
- short / mid / long / risk / liquidity / industry / fundamental feature symbols: 3676 each
- symbol coverage: 1.0 for all feature groups
- mandatory field coverage:
  - short horizon: 1.0
  - mid horizon: 1.0
  - long horizon: 0.98669
  - risk: 1.0
  - liquidity: 1.0
  - industry: 1.0
  - fundamental: 0.708806
- audit overall_passed=true
- blocking reasons: none
- no future leakage detected
- recommended next version: `v0.7.4-a-share-long-mid-short-scoring-system`

Primary artifacts:

- `data/equity_features/daily/2026-06-26/short_horizon_features.parquet`
- `data/equity_features/daily/2026-06-26/mid_horizon_features.parquet`
- `data/equity_features/daily/2026-06-26/long_horizon_features.parquet`
- `data/equity_features/daily/2026-06-26/risk_features.parquet`
- `data/equity_features/daily/2026-06-26/liquidity_features.parquet`
- `data/equity_features/daily/2026-06-26/industry_features.parquet`
- `data/equity_features/daily/2026-06-26/fundamental_features.parquet`
- `data/equity_features/daily/2026-06-26/feature_manifest.json`
- `data/equity_features/daily/2026-06-26/feature_field_coverage.json`
- `data/equity_features/daily/2026-06-26/feature_generation_summary.json`
- `data/equity_data_quality/a_share_multi_horizon_feature_audit.json`
- `outputs/audit/A_SHARE_MULTI_HORIZON_FEATURE_AUDIT.md`

Boundary:

- feature engineering only
- no stock scores generated
- no candidates generated
- no watchlist generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no model profit guarantee
- live trading readiness remains false

Validation: 1002 tests passed, 1 skipped.

## v0.7.2-a-share-tradable-universe-filter

This release adds the A-share tradable universe filter on top of the v0.7.1.2 full-market historical panels. It builds daily strict/caution/excluded/unknown buckets and an audit gate for future feature engineering. It is not a stock scoring, candidate generation, watchlist, portfolio, broker, or trading stage.

Includes:

- A-share tradable universe filter
- strict/caution/excluded/unknown universe buckets
- listing-age filter based on trading calendar age
- suspension and missing-price filter
- liquidity filter using 20d/60d average amount with explicit amount estimation flags
- market-cap filter with daily basic snapshot fallback when historical market-cap fields are unavailable
- low-price and price-sanity filters
- one-word limit up/down risk filter
- data coverage filter for 20d/60d/120d/250d history
- filter reason taxonomy and reason breakdown artifacts
- owner-facing tradable universe report
- tradable universe audit with boundary and forbidden-positive-wording checks

Audited result for `as_of_date=2026-06-26`:

- equity master symbols: 5867
- input symbols: 5867
- strict tradable count: 3676
- caution count: 0
- excluded count: 2191
- unknown status count: 0
- audit overall_passed=true
- blocking reasons: none
- warnings: 1
- recommended next version: `v0.7.3-a-share-multi-horizon-feature-engineering`

Boundary:

- no LongScore, MidScore, ShortScore, RiskScore, or LiquidityScore generated
- no candidates generated
- no watchlist generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no model profit guarantee
- live trading readiness remains false

Validation: 988 tests passed, 1 skipped.

## v0.7.1.2-a-share-historical-data-provider-expansion

This release resolves the v0.7.1.1 historical price coverage blocker by expanding the A-share historical backfill path from a limited/sample run to a full-market symbol queue sourced from `data/equity_universe/equity_master.parquet`.

Includes:

- root-cause diagnostic for the v0.7.1.1 10-symbol fail-closed result
- full-market A-share historical backfill symbol queue
- Eastmoney historical kline provider expansion with AkShare, BaoStock, Tushare, and local fallback adapters
- checkpoint/resume support for long full-market historical backfills
- per-batch manifests and per-symbol backfill manifest
- global coverage ratios against equity master and backfill queue
- readiness recommendation fix: failed readiness recommends `v0.7.1.3-a-share-historical-data-source-upgrade`, not `v0.7.2`
- updated historical coverage and feature-readiness audits

Audited coverage:

- equity master symbols: 5867
- backfill queue symbols: 5516
- price history symbols: 5516
- price history date range: `2021-01-04` to `2026-06-26`
- price history trading days: 1326
- symbols with 20d / 60d / 120d / 250d / 3y / 5y history: 5509 / 5474 / 5441 / 5379 / 5132 / 4458
- adjusted price symbols: 5516
- daily basic symbols: 5516
- financial symbols: 5211
- price history coverage vs equity master: 0.940174
- price history coverage vs queue: 1.0
- daily basic coverage vs equity master: 0.940174
- financial coverage vs equity master: 0.888188
- historical panel coverage audit overall_passed=true
- feature readiness audit overall_passed=true
- blocking reasons: none

Boundary:

- no stock scores generated
- no candidates generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no third-party code merged into the main flow
- no model profit guarantee
- live trading readiness remains false
- recommended next version is `v0.7.2-a-share-tradable-universe-filter`

Validation: 976 tests passed, 1 skipped.

## Unreleased: v0.7.1.1-a-share-historical-panel-backfill fail-closed

This implementation adds the A-share historical panel backfill workflow and readiness audits, but it is not released as a success tag because the current public historical provider run did not satisfy the minimum historical coverage gate.

Implemented:

- historical backfill plan
- daily price history panel writer
- adjusted price history panel writer with raw fallback labeling
- daily basic history panel writer with nullable field coverage
- partial quarterly financial history panel writer
- historical panel coverage audit
- feature readiness audit
- CLI commands for individual and one-command historical backfill
- documentation for historical backfill and feature readiness

Current fail-closed evidence:

- price history symbols: 10
- price history trading days: 841
- symbols with 120d history: 10
- symbols with 250d history: 10
- financial symbols: 1237
- financial quarter coverage ratio: 0.028407
- historical panel coverage audit overall_passed=false
- feature readiness audit overall_passed=false
- blocking reasons include `price_history_symbols_minimum=false`, `symbols_with_120d_history_minimum=false`, and `symbols_with_250d_history_minimum=false`
- no stock scores generated
- no candidates generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no model profit guarantee
- no live trading readiness claim

Validation: 961 tests passed, 1 skipped.

## v0.7.1-a-share-full-market-data-ingestion

This release adds the A-share full-market data ingestion foundation for the future AI stock selection line. It writes local master, calendar, market, industry, fundamental, source-manifest, coverage-audit, and schema-audit artifacts. It does not generate stock scores, candidates, watchlists, virtual portfolios, broker instructions, real orders, or official forward dry-run day2 artifacts.

Includes:

- A-share equity master for SSE/SZSE/BSE
- A-share trading calendar foundation
- daily price panel ingestion
- adjusted price panel ingestion with coverage tracking
- daily basic panel ingestion
- industry classification ingestion
- basic financials ingestion
- data source manifest
- coverage audit
- schema audit
- public provider fallback strategy documentation
- A-share data ingestion, schema, and quality-audit documentation

Audited & Validated scope:

- provider selected: `qstock_reference_public_http`
- source rows available: 5867
- source raw total: 5867
- source raw coverage ratio: 1.0
- equity master symbols: 5867
- observed exchanges: BSE, SSE, SZSE
- daily price symbols: 5513
- adjusted price symbols: 5513
- daily basic symbols: 5867
- industry symbols: 5867
- financial symbols: 5867
- min daily price date: `2026-06-26`
- max daily price date: `2026-06-26`
- trading days in calendar artifact: 282
- coverage audit passed with no blocking reasons
- schema audit passed with no blocking reasons
- warnings: raw adjusted-price fallback, board-level industry fallback, nullable basic financial numeric fields, and 354 master symbols missing daily price in the current public snapshot
- no stock scores generated
- no candidates generated
- no virtual portfolios generated
- official forward dry-run status unchanged
- day2 not executed
- run-daily not called
- no broker connected
- no real orders placed
- no third-party code merged into the main flow
- model profit not guaranteed
- recommended next version is `v0.7.2-a-share-tradable-universe-filter`

Validation: 951 tests passed, 1 skipped.

## v0.7.0-external-project-intake-and-a-share-selection-plan

This release opens the A-share full-market AI multi-horizon stock selection planning line. It downloads external research repositories into ignored `external_research/`, scans their README/license/source structure, writes an external intake report, generates an A-share full-market selection plan, produces a reuse matrix, and writes the v0.7 architecture and roadmap summary.

Includes:

- external research download script
- `external-project-intake` CLI
- `data/system/external_project_intake_report.json`
- `outputs/system/EXTERNAL_PROJECT_INTAKE_REPORT.md`
- `outputs/system/V0_7_ROADMAP_SUMMARY.md`
- `docs/A_SHARE_FULL_MARKET_AI_STOCK_SELECTION_PLAN.md`
- `docs/EXTERNAL_PROJECT_INTAKE.md`
- `docs/EXTERNAL_PROJECT_REUSE_MATRIX.md`
- `docs/V0_7_ARCHITECTURE.md`

Audited & Validated scope:

- external repos downloaded: 11
- AlphaSift classified A for full-market scanning, candidate ranking, and T+N evaluation reference
- qstock classified A for data adapters, WenCai-style screening, RPS/MM trend, fundamentals, and capital-flow reference
- daily_stock_analysis classified A for daily briefing, LLM summary, and notification reference
- guiwzh/stock classified A for long/short score weighting and stock score report reference
- Qlib classified B for ML workflow, RankIC/IC, and walk-forward evaluation reference
- AlphaEvo classified B for scoring weight optimization research
- easytrader, easyquotation, and easyquant classified D for future broker/quote/event adapter research
- THSTrader classified D for future Tonghuashun simulated trading adapter research
- zvt included as optional B/C architecture reference
- no third-party trading code merged into the main flow
- ETF forward dry-run status unchanged
- day2 not executed
- run-daily not called
- broker not connected
- real orders not placed
- LLM not used for trading decisions
- model profit not guaranteed
- recommended next version is `v0.7.1-a-share-full-market-data-ingestion`

Validation: 938 tests passed, 1 skipped.

## v0.6.3.2-forward-dry-run-day1-owner-report-pack

This release adds an owner-facing day1 report pack for the completed virtual forward dry-run day 1. It does not execute day2, does not execute day3, does not call `run-daily`, does not download real-time market data, does not call external market APIs, does not connect a broker, does not place real orders, and does not write main orders/trades/portfolio/accounts.

Includes:

- day1 owner report scope plan
- day1 owner summary report
- day1 strategy signal explanation
- day1 virtual order and fill report
- day1 isolated ledger report
- day1 data reproducibility appendix
- day1 continuation blocker note
- day1 owner report pack summary
- day1 owner report audit

Audited & Validated scope:

- day1 completed
- day1 as_of_date is `2026-06-25`
- `strategies_total=3`
- `strategies_generated=3`
- virtual order preview produced 16 orders
- virtual execution produced 16 fills and 0 rejects
- owner report pack complete
- owner report audit passed with no blocking reasons
- day2 not executed
- day3 not executed
- run-daily not called
- real-time market data not downloaded
- external API not called
- main orders/trades/portfolio/accounts not written
- broker not connected
- real orders not placed
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not strategy effectiveness proof
- not full forward dry-run validation
- not live trading readiness
- recommended next version is `v0.6.3.3-forward-dry-run-data-horizon-extension`

Validation: 935 tests passed, 1 skipped.

## v0.6.3.1-forward-dry-run-day1-continuation-artifacts

This release absorbs the v0.6.4 blocking preflight and materializes the missing v0.6.3 day1 continuation artifacts required before a future day2 continuation attempt. It does not execute day2, does not execute day3, does not call `run-daily`, does not connect a broker, does not place real orders, and does not write main orders/trades/portfolio/accounts.

Includes:

- day1 continuation gap analysis
- day1 artifact manifest
- day1 reproducibility manifest
- day2 readiness packet
- day2 continuation gate preview
- day1 continuation artifact audit
- day1 continuation reclassification v0631

Audited & Validated scope:

- v0.6.4 blocking preflight absorbed
- missing continuation artifact gap resolved
- `day1_artifact_manifest` generated
- `day1_reproducibility_manifest` generated
- `day2_readiness_packet` generated
- `day2_continuation_gate_preview` generated
- continuation artifact audit passed with no blocking reasons
- `continuation_artifact_gap_resolved=true`
- `remaining_continuation_artifact_gap_count=0`
- `day2_blocker_count=0`
- recommended next version is `v0.6.4-forward-dry-run-day2-continuation`
- day2 not executed
- day3 not executed
- run-daily not called
- main orders/trades/portfolio/accounts not written
- broker not connected
- real orders not placed
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not strategy effectiveness proof
- not full forward dry-run validation
- not live trading readiness

Validation: full pytest passed with 1 skipped.

## v0.6.3-forward-dry-run-day1-executed-audited

This release executes virtual isolated forward dry-run day 1 after owner authorization materialization. It starts the forward dry-run ledger for day 1 only. It does not call `run-daily`, does not connect a broker, does not place real orders, does not write the main orders/trades/portfolio/accounts ledger, and does not complete the 30-day forward dry-run.

Includes:

- day1 pre-execution gate with git-clean, authorization, data, protected-path, and no broker/live guard checks
- day1 input snapshot from local authorized historical data as of 2026-06-25
- day1 baseline strategy signals for all three baseline strategies
- day1 virtual order preview with T+1, tradability, lot, and cost checks
- day1 virtual execution result in `forward_dry_run_virtual` mode
- isolated forward dry-run ledger snapshot
- day1 risk and boundary report
- day1 operator report
- post-execution audit
- forward dry-run status
- day1 blocker reclassification v063

Audited & Validated scope:

- pre-execution gate passed
- latest eligible local as-of date: 2026-06-25
- `strategies_total=3`
- `strategies_generated=3`
- virtual order preview produced 16 orders and 0 rejects
- virtual execution produced 16 fills and 0 rejects
- `forward_dry_run_started=true`
- `forward_dry_run_days_completed=1`
- `next_day_index=2`
- isolated forward dry-run ledger written
- main ledger not written
- broker not connected
- real orders not placed
- labels not used
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not full forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness

Validation: 890 tests passed, 1 skipped.

## v0.6.2.1-owner-manual-confirmation-materialized

This release materializes owner manual confirmation for the forward dry-run start authorization flow. It makes the system eligible for a future day1 prompt request, but it does not start forward dry-run day 1, does not call `run-daily`, does not generate a day1 execution prompt, and does not write the main ledger.

Includes:

- owner manual confirmation record
- completed manual confirmation checklist v2
- authorized owner packet for day1 prompt generation
- start gate revalidation
- day1 prompt eligibility revalidation
- authorization materialization audit
- day1 blocker reclassification v0621

Audited & Validated scope:

- `manual_confirmation_complete=true`
- `forward_dry_run_start_authorized=true`
- `day1_prompt_eligible=true`
- `day1_prompt_generated=false`
- `day1_start_allowed=false`
- `run-daily` not called
- forward dry-run not started
- main ledger not written
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness

Validation: 877 tests passed, 1 skipped.

## v0.6.2-forward-dry-run-start-authorization-pack-audited

This release creates the fail-closed start authorization pack required before any future forward dry-run day 1. It does not start forward dry-run, does not call `run-daily`, does not write the main orders/trades/portfolio/accounts ledger, and does not generate an executable day1 prompt.

Includes:

- forward dry-run authorization scope plan
- start prerequisite inventory
- current daily workflow readiness snapshot
- manual confirmation checklist v2
- owner authorization packet
- start gate validator
- run-daily command preview metadata
- day1 prompt eligibility report
- start authorization audit
- day1 blocker reclassification v062

Audited & Validated scope:

- technical prerequisites are present
- manual confirmation defaults false
- owner authorization defaults false
- `day1_start_allowed=false`
- `day1_prompt_eligible=false`
- `day1_prompt_generated=false`
- `run-daily` not called
- forward dry-run not started
- main ledger not written
- labels not used as authorization
- ML shadow not used as authorization
- LLM not used for trading decision
- RL not used
- promotion not triggered
- not forward dry-run validation
- not strategy effectiveness proof
- not live trading readiness

Validation: 862 tests passed, 1 skipped.

## v0.6.1-daily-workflow-binding-audited

This release binds the v0.6.0 baseline strategy pack and v0.5.9 virtual execution rules into a repeatable daily research preview workflow. Daily workflow binding is research-only preview infrastructure and does not start forward dry-run. It uses local authorized historical daily data snapshots, does not download real-time market data, does not call `run-daily`, and does not write the main orders/trades/portfolio/accounts ledger.

Includes:

- daily workflow scope plan
- daily market data snapshot contract
- latest available trading date detection from local data
- daily data freshness/completeness audit
- daily input freeze manifest with file hashes
- daily baseline signal binding
- daily order preview binding
- daily isolated execution preview
- daily report packet
- protected path residue scanner
- daily workflow audit
- day1 blocker reclassification v061

Audited & Validated scope:

- `daily-workflow-scope-plan` confirmed v0.6.0 baseline strategy pack completeness and kept day 1 disallowed.
- `daily-market-data-snapshot --as-of-date 2024-12-31` generated a local historical snapshot without external download.
- `audit-daily-data-quality` passed with universe coverage complete and risk proxy available; missing direct benchmark rows for CSI500, CSI1000, and CHINEXT are recorded as warnings.
- `daily-input-freeze-manifest` recorded hashes for market data, benchmark data, risk proxy, baseline contracts, strategy registry, virtual execution, calendar, price status, lot position, cost contract, data quality audit, and snapshot.
- `daily-baseline-signals --strategy all` generated daily signals for all three baseline strategies.
- `daily-order-preview --strategy all --execution-mode isolated` generated preview-only order proposals with `executed=false`.
- `daily-isolated-execution-preview --execution-mode isolated` generated state-free preview fills, rejects, costs, and valuation estimates with `execution_mode=isolated_preview`.
- `daily-report-packet` generated the operator-facing research preview packet with explicit non-claims.
- `protected-path-residue-scan` classified ignored runtime residue as nits and produced blocker count 0.
- `audit-daily-workflow` passed with no blocking reasons and recommends `v0.6.2-forward-dry-run-start-authorization-pack`.
- `reclassify-day1-blockers-after-daily-workflow` kept `day1_start_allowed=false`, `manual_confirmation_complete=false`, and `forward_dry_run_start_authorized=false`.
- `run-daily` was not called.
- Forward dry-run was not started or validated.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Labels, ML shadow, LLM, RL, experiments, and promotion outputs were not used as authorization.
- Promotion was not triggered.
- Historical preview output is not strategy effectiveness proof.
- This release is not forward dry-run validation and not live trading readiness.

Validation: 839 tests passed, 1 skipped.

## v0.6.0-baseline-strategy-pack-audited

This release adds a research-only baseline strategy pack for future forward dry-run preparation. Baseline strategy pack is research-only and does not start forward dry-run. It does not call `run-daily`, does not write the main orders/trades/portfolio/accounts ledger, does not use labels, ML shadow, LLM, RL, experiments, or promotion outputs as authorization, and does not prove strategy effectiveness or certify live trading readiness.

Includes:

- baseline strategy scope plan
- baseline strategy contract
- baseline strategy registry and parameter versions
- `equal_weight_etf_rotation`
- `momentum_risk_adjusted_rotation`
- `defensive_cash_rotation`
- PIT-safe baseline strategy signals
- baseline order previews with `preview_only=true` and `executed=false`
- isolated baseline strategy replay using v0.5.9 virtual execution rules
- benchmark comparison
- baseline strategy reports
- baseline strategy pack summary
- baseline strategy pack audit
- day1 blocker reclassification v060

Audited & Validated scope:

- `baseline-strategy-scope-plan` confirmed v0.5.9 execution blockers are closed and v0.6.0 is not day 1.
- `baseline-strategy-contract` generated machine-readable input, output, PIT, forbidden-input, forbidden-claim, and boundary requirements.
- `baseline-strategy-registry` registered three deterministic rule-based strategies and parameter versions.
- `generate-baseline-strategy-signals --strategy all --start-date 2024-01-02 --end-date 2024-12-31` generated PIT-safe after-close signals with T+1 earliest execution.
- `build-baseline-order-preview --strategy all --execution-mode isolated` generated preview-only proposals.
- `replay-baseline-strategy --strategy all --execution-mode isolated` wrote isolated strategy replay orders/trades/portfolio/valuations under `data/replays/strategies/`.
- `compare-baseline-strategy-benchmarks --strategy all` generated benchmark comparison for CSI300, CSI500, CSI1000, CHINEXT, HSI, HSTECH, CASH, and EQUAL_ETF.
- `baseline-strategy-report --strategy all` generated one report per strategy with explicit non-claims.
- `baseline-strategy-pack-summary` passed with `all_strategies_complete=True`.
- `audit-baseline-strategy-pack` passed with no blocking reasons.
- `reclassify-day1-blockers-after-baseline-strategies` produced `updated_day1_blocker_count=0` and recommends `v0.6.1-daily-workflow-binding`.
- `run-daily` was not called.
- Forward dry-run was not started or validated.
- Main orders/trades/portfolio/accounts ledgers were not written.
- ML shadow was not used as authorization.
- LLM was not used for trading decision.
- RL was not used.
- Promotion was not triggered.
- Historical performance is not strategy effectiveness proof.
- This release is not live trading readiness.

Validation: 811 tests passed, 1 skipped.

## v0.5.9-ashare-execution-rules-hardened

This release hardens A-share / ETF virtual execution rules for future forward dry-run preparation. v0.5.9 hardens virtual execution rules but does not start forward dry-run. It does not call `run-daily`, does not write the main orders/trades/portfolio/accounts ledger, does not prove strategy effectiveness, and does not certify live trading readiness.

Includes:

- A-share / ETF trading calendar contract for SSE / SZSE / HKEX
- T-day signal / T+1 execution semantics
- suspension / missing price / limit up / limit down handling
- ST / new listing handling
- board lot / odd lot rules
- fee / tax / slippage model
- cash / position / available shares accounting
- virtual execution contract
- isolated ledger invariant audit
- execution-aware replay smoke
- day1 blocker reclassification

Audited & Validated scope:

- `ashare-execution-gap-plan` read v0.5.8.1 blocker artifacts and targeted three execution blockers.
- `ashare-trading-calendar-audit` passed for SSE, SZSE, HKEX, explicit holidays, weekends, and HKEX/A-share calendar differences.
- `execution-timeline-contract` rejects same-day execution for T-day close signals and rejects future prices.
- `ashare-price-status-contract` handles suspended, missing price, limit up, limit down, ST, new listing, delisting risk, and unknown status fail-closed.
- `ashare-lot-and-position-contract` defines board lot, odd lot sell, T+1 available shares, and cash/position invariants.
- `ashare-execution-cost-contract` defines commission, minimum commission, stamp duty, slippage, and PIT-safe fill price rules.
- `virtual-execution-contract` integrates calendar, T+1, tradability, lot, cash/position, costs, reject reasons, fill reasons, isolated output paths, and protected path guard.
- `audit-isolated-ledger-invariants` passed.
- `execution-aware-replay-smoke` passed in isolated mode.
- `reclassify-day1-blockers-after-execution-hardening` closed the three execution blockers and recommends `v0.6.0-baseline-strategy-pack`.
- `audit-ashare-execution-rules` passed with no blocking reasons.
- `run-daily` was not called.
- Forward dry-run was not started or validated.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Labels, ML shadow, experiments, LLM, RL, and promotion outputs were not used as authorization.

Validation: 787 tests passed, 1 skipped.

## v0.5.8.1-plan-alignment-and-mvp-gap-audited

This patch release adds plan alignment and MVP gap audit artifacts. Plan alignment is an audit, not day 1 authorization. It does not start forward dry-run, does not call `run-daily`, and does not write the main orders/trades/portfolio/accounts ledger.

Includes:

- plan checklist extractor
- MVP requirement map
- artifact coverage scanner
- MVP gap classifier
- day-1 blocker classifier
- next work register
- plan alignment audit

Audited & Validated scope:

- `plan-checklist` extracted R001-R024 MVP requirements.
- `mvp-requirement-map` mapped each requirement to candidate module, CLI, test, artifact, report, audit, doc, or release-tag evidence.
- `artifact-coverage-scanner` scanned repo artifacts as metadata only.
- `classify-mvp-gaps` classified all 24 requirements.
- `classify-day1-blockers` generated day-1 blocker status while keeping day 1 disallowed by default.
- `next-work-register` generated the recommended next version.
- `audit-plan-alignment` passed with `overall_passed=True` and no blocking reasons.
- `run-daily` was not called.
- Forward dry-run was not started.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Labels were not used as authorization.
- ML shadow was not used as day-1 authorization.
- LLM was not used for trading decision.
- RL was not used.
- Promotion was not triggered.
- Historical performance is not strategy effectiveness proof.

Validation: 755 tests passed, 1 skipped.

## v0.5.8-day0-operational-readiness-audited

This release adds the day-0 operational readiness pack for a future 30 trading-day forward dry-run. Day-0 readiness does not start forward dry-run. Historical data authorization is not trading authorization.

Includes:

- day-0 data freeze manifest
- accepted warning register
- blocking condition register
- run-daily preflight checklist with command preview only
- manual confirmation packet with all confirmation fields default false
- forward dry-run operating calendar and daily log template
- day-0 readiness report
- day-0 readiness audit

Audited & Validated scope:

- `day0-data-freeze` generated frozen input package records and accepted known EPU/OECD limitations.
- `day0-warning-register` classified remaining v0.5.7.1 warnings and produced `blocking_count=0`.
- `day0-blocking-conditions` produced `current_blocking_count=0` while keeping manual confirmation required.
- `day0-run-daily-preflight` generated a preview-only `run-daily` command with `executed=false`.
- `day0-manual-confirmation-packet` kept `manual_confirmation_complete=false` and `forward_dry_run_start_authorized=false`.
- `forward-dry-run-operating-calendar` generated a template-only 30 day operating calendar and daily log template.
- `day0-readiness-report` produced `overall_status=ready_for_manual_confirmation`.
- `audit-day0-readiness` passed with `overall_passed=True` and no blocking reasons.
- EPU partial limitation is recorded.
- OECD macro-cycle proxy limitation is recorded and not described as official OECD CLI.
- Internal global-briefing historical package remains `not_configured`.
- Proxy package is not an internal global-briefing signal.
- Main orders/trades/portfolio/accounts ledgers were not written.
- `run-daily` was not called.
- Labels, ML shadow, experiments, promotion outputs, broker/live integration, RL, and LLM trading decisions were not used.

Boundaries remain strict: day-0 readiness is not forward dry-run validation, not strategy effectiveness proof, not live trading readiness, not trading authorization, not broker integration, and not promotion approval.

Validation: 737 tests passed, 1 skipped.

## v0.5.7.1-historical-data-gap-closure-audited

This patch release closes v0.5.7 historical research data gaps and reduces warning noise for the authorized full historical proxy replay path. Historical data authorization is not trading authorization.

Includes:

- historical warning inventory with category, severity, grouped counts, and fix status
- EPU package repair through authorized/local/API/FRED-compatible sources, with policy-uncertainty proxy fallback when official source access is unavailable
- OECD CLI repair through authorized/local/API sources, with authorized macro-cycle proxy fallback explicitly marked as not official OECD CLI
- full historical proxy package rebuild with EPU and macro-cycle fields
- normalized proxy package rebuild and signal contract validation
- full historical proxy replay grouped warning output with raw warning count preserved
- gap closure workflow, gap closure report, and gap closure release audit

Audited & Validated scope:

- `close-historical-data-gaps --start-date 2018-01-01 --end-date latest --replay-start-date 2024-01-02 --replay-end-date 2024-12-31 --min-coverage 0.80 --continue-on-error` passed.
- Available packages improved from 6/9 to at least 8/9 while keeping the optional authorized global-briefing historical signal package separately reported.
- EPU was repaired or represented by a clearly marked policy-uncertainty proxy.
- OECD CLI was repaired or represented by a clearly marked authorized macro-cycle proxy that is not official OECD CLI.
- `historical-warning-inventory` generated JSON and Markdown with unknown warnings reduced to zero.
- `run-full-historical-proxy-replay` retained raw warning counts and displayed grouped warnings.
- `historical-data-gap-closure-report` generated JSON and Markdown.
- `audit-historical-data-gap-closure` passed with `overall_passed=True` and no blocking reasons.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Isolated replay artifacts were written under `data/replays/global_briefing/`.
- `run-daily` was not called.
- Labels, ML shadow, experiments, promotion outputs, broker/live integration, RL, and LLM trading decisions were not used.
- Forward dry-run was not started or validated.

Boundaries remain strict: this is historical data gap closure only, not broker integration, not live trading, not forward dry-run validation, not strategy effectiveness proof, not live trading readiness, not production global-briefing package validation, and not promotion approval.

Validation: 716 tests passed, 1 skipped.

## v0.5.7-authorized-full-historical-data-acquisition-audited

This release adds authorized full historical data package acquisition for the global-briefing research replay path. It downloads or loads historical packages, normalizes them, builds a unified proxy package, audits quality, runs isolated proxy replay, and produces acquisition reports. Historical data authorization is not trading authorization.

Includes:

- authorized full historical data package acquisition
- ETF OHLCV package
- benchmark index package
- FX / USD-CNY package
- VIX / global risk package
- rates / liquidity package
- commodity / inflation risk package
- policy uncertainty / EPU package status and warnings
- OECD CLI / macro cycle package status and warnings
- optional authorized global-briefing historical signal package status
- unified global-briefing-compatible proxy package
- historical data quality audit
- full historical proxy isolated replay workflow
- historical data acquisition report
- historical data acquisition audit

Audited & Validated scope:

- `download-historical-data-packages --start-date 2018-01-01 --end-date latest --continue-on-error` generated package manifests and provenance.
- ETF, benchmark, FX/USD-CNY, VIX, rates/liquidity, and commodity/inflation packages downloaded with checksums.
- EPU and OECD CLI package attempts failed soft with explicit warnings.
- Authorized global-briefing historical signal package was `not_configured` and non-blocking.
- `normalize-historical-data-packages` built and validated `GB-AUTHORIZED-FULL-HISTORICAL-PROXY-V1`.
- `audit-historical-data-quality` passed with `overall_passed=True`.
- `run-full-historical-proxy-replay --execution-mode isolated` completed with `overall_status=research_review_ready`.
- `historical-data-acquisition-report` generated acquisition JSON and Markdown.
- `audit-historical-data-acquisition` passed with `overall_passed=True` and no blocking reasons.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Isolated replay artifacts were written under `data/replays/global_briefing/`.
- `run-daily` was not called.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.
- Forward dry-run was not started or validated.

Boundaries remain strict: historical data authorization is not trading authorization, proxy signals are not internal global-briefing signals, production global-briefing package status is separately reported, historical replay is not forward dry-run validation, historical replay is not strategy effectiveness proof, the system is not live trading ready, no broker/live/RL/LLM decision capability was added, and no real orders are supported.

Validation: 698 tests passed, 1 skipped.

## v0.5.6.1-warning-triage-evidence-quality

This patch release adds evidence-quality reporting around the v0.5.6 real-package-style global-briefing integration artifacts. It does not add replay functionality or trading functionality.

Includes:

- warning triage for v0.5.6 artifacts
- evidence quality report
- production global-briefing package acceptance criteria
- evidence quality audit
- explicit clarification that `GB-REAL-FIXTURE` is not a production package

Audited & Validated scope:

- `global-briefing-warning-triage` generated warning triage JSON and Markdown.
- `global-briefing-evidence-quality-report` generated evidence quality JSON and Markdown.
- `global-briefing-production-acceptance-criteria` generated machine-readable criteria, system Markdown, and docs Markdown.
- `audit-global-briefing-evidence-quality` passed with `overall_passed=True`.
- Blocking reasons: none.
- Production readiness remains `false`.
- Recommended production minimum coverage is `0.80`.
- Recommended production target coverage is `0.90`.
- Main orders/trades/portfolio/accounts ledgers were not written.
- `run-daily` was not called.
- No network request was used.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.
- Forward dry-run was not started or validated.

Boundaries remain strict: evidence-quality only, `GB-REAL-FIXTURE` is not a production package, production global-briefing historical coverage is not validated, strategy effectiveness is not proven, forward dry-run is not validated, live trading readiness is not certified, no broker, no real orders, no promotion, no RL trading, and no LLM trading decisions.

Validation: 669 tests passed, 1 skipped.

## v0.5.6-real-global-briefing-signal-integration-audited

This release adds the local real global-briefing historical signal package integration layer on top of the audited isolated replay adapter.

Includes:

- local global-briefing package manifest generation
- real package normalization to the v1 signal contract
- package coverage and point-in-time audit
- real package isolated replay workflow
- integration report
- real package integration release audit
- fixture-based local package inputs for JSONL/CSV and point-in-time checks

Audited & Validated scope:

- `global-briefing-package-manifest --root tests/fixtures/global_briefing_real` found local package files.
- `normalize-global-briefing-package` generated `data/global_briefing/normalized/GB-REAL-FIXTURE.normalized.jsonl`.
- `audit-global-briefing-package-coverage` passed with `coverage_ratio=0.6` and no blocking reasons.
- `run-global-briefing-real-package-replay --execution-mode isolated` completed with `overall_status=research_review_ready`.
- `global-briefing-real-package-report` produced `overall_status=research_review_ready`.
- `audit-global-briefing-real-package-integration` passed with `overall_passed=True`.
- Blocking reasons: none.
- Main orders/trades/portfolio/accounts ledgers were not written.
- Only isolated replay ledger artifacts were written under `data/replays/global_briefing/`.
- `run-daily` was not called.
- No network request was used.
- Labels, ML shadow, experiments, promotion outputs, RL, and LLM trading decisions were not used.
- Forward dry-run was not started or validated.

Boundaries remain strict: local historical package integration only, not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, no broker, no real orders, no strategy state or parameter changes, no promotion, no RL trading, and no LLM trading decisions.

Validation: 633 tests passed, 1 skipped.

## v0.5.5-isolated-replay-execution-adapter-audited

This release adds the isolated replay execution adapter for global-briefing historical replay. The fixture E2E path no longer uses the no-trade fallback; it generates isolated virtual signals, orders, trades, portfolio, account, valuations, and summary artifacts under `data/replays/global_briefing/`.

Includes:

- isolated replay state model
- global-briefing signal-to-target adapter
- isolated order/execution/valuation adapter
- isolated replay ledger writer
- replay runner isolated execution mode
- replay evaluation upgrade
- isolated replay adapter audit

Audited & Validated scope:

- `replay-global-briefing-history --execution-mode isolated` generated isolated execution artifacts.
- `execution.mode=isolated`.
- `no_trade_fallback=false`.
- Isolated account, signals, orders, trades, portfolio, and valuations outputs exist.
- All isolated replay ledger outputs are under `data/replays/global_briefing/`.
- Main ledger not written.
- run-daily not called.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.
- `audit-isolated-replay-adapter` passed with `overall_passed=True`.
- Blocking reasons: none.

Boundaries remain strict: not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, no broker, no real orders, no strategy state or parameter changes, no RL trading, and no LLM trading decisions.

Validation: 572 tests passed, 1 skipped.

## v0.5.4-global-briefing-historical-replay-harness-audited

This release adds the full global-briefing historical replay harness. It establishes a repeatable, auditable, isolated replay framework for future historical macro signal packages.

Includes:

- global-briefing signal contract
- signal package validator
- point-in-time replay bundle
- isolated historical replay harness
- replay evaluation report
- replay audit
- fixture-based end-to-end smoke inputs for signal and price packages

Audited & Validated scope:

- `global-briefing-contract` generated contract JSON and Markdown.
- `validate-global-briefing-signals` passed on the fixture signal package.
- `build-global-briefing-replay-bundle` generated a point-in-time bundle with `future_signal_used=False`.
- `replay-global-briefing-history` generated an isolated no-trade replay summary.
- `global-briefing-replay-report` produced `overall_status=research_review_ready`.
- `audit-global-briefing-replay` passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- Main ledger not written.
- run-daily not called.
- Labels, ML shadow, experiments, and promotion outputs were not used.
- Promotion was not triggered.

Boundaries remain strict: not forward dry-run validation, not live trading readiness, not strategy effectiveness proof, no broker, no real orders, isolated replay only, no strategy state or parameter changes, no RL trading, and no LLM trading decisions.

Validation: 518 tests passed, 1 skipped.

## v0.5.3-forward-dry-run-readiness-audited

This release adds a readiness-only audit for preparing a future 30 trading-day virtual forward dry-run. It does not start or validate the forward dry-run.

Includes:

- forward dry-run readiness audit
- day-0 checklist
- 30 trading-day forward plan
- protected path snapshot
- run-daily isolation check
- future-data leakage readiness check
- artifact separation check
- readiness-only safety boundary report

Audited & Validated scope:

- `forward-dry-run-readiness --trading-days 30` generated JSON and Markdown.
- Day-0 checklist and 30 trading-day plan were generated.
- Readiness audit passed with `overall_passed=True`.
- Blocking reasons: none.
- Warning: trading calendar not found; manual calendar confirmation is required before day 1.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called by the readiness validation flow.

Boundaries remain strict: readiness-only, dry-run not started, dry-run not validated, no live trading, no broker, no real orders, no auto promotion, no strategy state or parameter changes, no main ledger writes, no RL trading, no LLM trading decisions, and no strategy effectiveness proof.

Validation: 435 tests passed, 1 skipped.

## v0.5.2-usability-polish

This release adds usability polish for finding reports, locating current artifacts, and resuming project work. It does not add trading functionality.

Includes:

- corrected final handoff wording
- report index
- latest artifact locator
- artifact browser
- quick status
- command cookbook
- usability audit

Audited & Validated scope:

- `final-handoff-review` regenerated with corrected pytest and candidate wording.
- `report-index --include-audit --include-experiments --include-system` generated JSON and Markdown.
- `latest-artifact --type handoff` and `latest-artifact --type all` generated locator output.
- `artifact-browser` generated JSON and Markdown.
- `quick-status` generated JSON and Markdown.
- `usability-audit` passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called by the usability validation flow.

Boundaries remain strict: no trading functionality added, no live trading, no broker integration, no real orders, no auto promotion, no strategy state or parameter changes, no RL trading, and no LLM trading decisions. Forward 30d dry-run is still not completed.

Validation: 410 tests passed, 1 skipped.

## v0.5.1-system-integrity-and-documentation

This release consolidates system integrity documentation and auditability without adding trading capability.

Includes:

- documentation consolidation across README and docs/
- CLI inventory
- artifact inventory
- system smoke test
- boundary regression audit
- system integrity audit

Audited & Validated scope:

- `cli-inventory` generated JSON and Markdown.
- `artifact-inventory` generated JSON and Markdown.
- `system-smoke-test --include-reports --include-inventory` passed.
- `boundary-regression-audit` passed.
- `system-integrity-audit` passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called by the system integrity validation flow.

Boundaries remain strict: no live trading, no broker integration, no real orders, no auto promotion, no strategy state or parameter changes, no RL trading, and no LLM trading decisions. Forward 30d dry-run is still not completed.

Validation: 374 tests passed, 1 skipped.

## v0.5.1-validation-gap-remediation

This patch release remediates selected v0.5 validation gaps without expanding the trading scope.

Includes:

- `project_timezone` changed from `Asia/Tokyo` to `Asia/Shanghai`.
- `max_daily_turnover` is now enforced by the risk engine.
- `mistake_pattern_library.json` now includes explicit diagnostic boundary metadata.
- v0.5.1 remediation JSON and Markdown audit artifacts.

Deferred gaps:

- Market-rule-aware execution remains deferred to v0.6.
- Generalized Point-in-Time schema remains deferred to v0.7.

Boundaries remain strict: no broker integration, no live trading, no active promotion, no strategy state or parameter changes, no main ledger writes, no RL trading, and no LLM trading decisions. The v0.5.0 tag was not moved.

Validation: 345 tests passed, 1 skipped.

## v0.5.0-research-reporting-control-plane-audited

This release adds the v0.5 research reporting and control plane.

Includes:

- weekly research report
- monthly research report
- system dashboard
- project status report
- one-command research reporting pipeline
- reporting system release audit

Audited & Validated scope:

- Weekly and monthly reports generated from existing artifacts.
- System dashboard and project status reports generated.
- Research pipeline generated all v0.5 reporting artifacts.
- Reporting system audit passed with `overall_passed=True`.
- Blocking reasons: none.
- Protected orders/trades/portfolio/accounts paths unchanged.
- `run-daily` was not called or modified by the reporting pipeline.
- The reports remain research-only and do not validate forward 30d dry-run.

Boundaries remain strict: no broker integration, no live trading, no active promotion, no strategy state or parameter changes, no main ledger writes, no RL trading, and no LLM trading decisions.

Validation: 330 tests passed, 1 skipped.

## v0.3.0-ml-shadow-pipeline-audited

This release adds the ML shadow research pipeline v1 (audited).

Includes:

- feature store v1
- label versioning v1
- walk-forward dataset builder
- ML shadow model scaffold
- ML prediction output
- ML shadow signal generator
- ML shadow leaderboard
- ML shadow research report

Audited & Validated scope:

- Walk-forward dataset builder validated.
- ML shadow model training and inference scaffold verified.
- ML shadow prediction file output (predictions.jsonl) successfully written.
- ML shadow signal generator (ml_shadow_signals.jsonl) successfully generated.
- ML shadow leaderboard recommendation generated as "watch".
- ML shadow research report successfully compiled.
- Independent boundaries audited (no broker connections, no live-trading logic, no main ledger pollution).
- Data leakage: none (chronological split enforced).
- Audit verdict: PASS_WITH_NO_ACTION.

Boundaries remain strict: no broker integration, no live trading, no active ML signals execution, no active ledger pollution.

Validation: 188 tests passed.

## v0.2.1-price-only-historical-replay-validated

This release adds historical 30-trading-day price-only replay validation.

Validated scope:

- Historical 30-trading-day price-only replay passed.
- Replay date range: 2026-05-11 to 2026-06-22.
- `historical_replay_passed=True`.
- `price_only_replay=True`.
- `forward_30d_dry_run_passed=False`.
- No real macro_signals were available.
- Replay did not pollute main daily-run ledger.
- Critical errors: 0.

This release is not a full historical global-briefing replay and is not future 30-day forward dry-run validation. Boundaries remain strict: no broker integration, no live trading, no real orders, no ML, no RL, and no LLM trading decisions.

Validation: 144 tests passed.

## v0.2.0-historical-real-data-validated

This release marks Trading Core as a historical real-data validated, file-backed virtual trading research base.

Validated scope:

- Historical real ETF data validation passed.
- Batch backtest passed.
- Backtest consistency passed.
- Real-data validation report passed.
- `dry_run_30d_passed=False`.
- Blocking reason: `actual_run_days_below_30`, `missing_real_global_briefing_inputs`.

This release does not represent 30-day real global-briefing dry-run validation. Boundaries remain strict: no broker integration, no live trading, no real orders, no ML, no RL, and no LLM trading decisions.

Validation: 136 tests passed.

## v0.1.0-core-hardened

This release freezes the first hardened version of Trading Core as a file-backed virtual trading research base.

It supports daily dry-runs, runtime health files, ETF historical CSV import, strategy backtests, admission decisions, global-briefing summary export, and throttled evolution artifacts.

Boundaries remain strict: no broker integration, no live trading, no real orders, no ML, no RL, and no LLM trading decisions.

Freeze scope: Issue 1-36 complete.

Validation: 83 tests passed.
