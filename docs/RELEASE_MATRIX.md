# Release Matrix

Note: `v0.5.1-validation-gap-remediation` is a narrow patch on the v0.5 line. The current isolated replay adapter line is `v0.5.5-isolated-replay-execution-adapter-audited`.

| Version | Tag | Scope | Passed | Limitations |
| ------- | --- | ----- | ------ | ----------- |
| v0.1.0-core-hardened | v0.1.0-core-hardened | trading core hardened | yes | virtual file-backed only |
| v0.2.0-historical-real-data-validated | v0.2.0-historical-real-data-validated | historical real ETF data validation | yes | forward 30d dry-run not completed |
| v0.2.1-price-only-historical-replay-validated | v0.2.1-price-only-historical-replay-validated | 30-trading-day price-only historical replay | yes | not full global-briefing replay |
| v0.3.0-ml-shadow-pipeline-audited | v0.3.0-ml-shadow-pipeline-audited | ML shadow research pipeline audited | yes | shadow only, not active trading |
| v0.4.0-strategy-experiment-system-audited | v0.4.0-strategy-experiment-system-audited | strategy experiment system audited | yes | no promotion, no live trading |
| v0.5.0-research-reporting-control-plane-audited | v0.5.0-research-reporting-control-plane-audited | research reporting and control plane audited | yes | reporting does not prove strategy effectiveness |
| v0.5.1-validation-gap-remediation | v0.5.1-validation-gap-remediation | selected validation gap remediation patch | yes | market-rule-aware execution and generalized PIT schema deferred |
| v0.5.1-system-integrity-and-documentation | v0.5.1-system-integrity-and-documentation | documentation, inventory, smoke, and boundary audits | yes | no new trading capability |
| v0.5.2-usability-polish | v0.5.2-usability-polish | report index, latest artifact locator, artifact browser, quick status, command cookbook, usability audit | yes | no new trading capability; forward 30d dry-run still not completed |
| v0.5.3-forward-dry-run-readiness-audited | v0.5.3-forward-dry-run-readiness-audited | forward dry-run readiness audit, day-0 checklist, 30D plan, protected path and leakage checks | yes | readiness only; forward dry-run not started or validated |
| v0.5.4-global-briefing-historical-replay-harness-audited | v0.5.4-global-briefing-historical-replay-harness-audited | global-briefing signal contract, package validation, point-in-time bundle, isolated historical replay, evaluation, and audit | yes | historical replay harness only; not forward dry-run validation, not live trading readiness, not strategy effectiveness proof |
| v0.5.5-isolated-replay-execution-adapter-audited | v0.5.5-isolated-replay-execution-adapter-audited | isolated replay state model, signal-to-target adapter, virtual order/execution/valuation adapter, ledger writer, evaluation upgrade, and adapter audit | yes | isolated execution adapter only; not forward dry-run validation, not live trading readiness, not strategy effectiveness proof |
