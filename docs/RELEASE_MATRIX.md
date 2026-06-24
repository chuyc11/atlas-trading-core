# Release Matrix

| Version | Tag | Scope | Passed | Limitations |
| ------- | --- | ----- | ------ | ----------- |
| v0.1.0-core-hardened | v0.1.0-core-hardened | trading core hardened | yes | virtual file-backed only |
| v0.2.0-historical-real-data-validated | v0.2.0-historical-real-data-validated | historical real ETF data validation | yes | forward 30d dry-run not completed |
| v0.2.1-price-only-historical-replay-validated | v0.2.1-price-only-historical-replay-validated | 30-trading-day price-only historical replay | yes | not full global-briefing replay |
| v0.3.0-ml-shadow-pipeline-audited | v0.3.0-ml-shadow-pipeline-audited | ML shadow research pipeline audited | yes | shadow only, not active trading |
| v0.4.0-strategy-experiment-system-audited | v0.4.0-strategy-experiment-system-audited | strategy experiment system audited | yes | no promotion, no live trading |
| v0.5.0-research-reporting-control-plane-audited | v0.5.0-research-reporting-control-plane-audited | research reporting and control plane audited | yes | reporting does not prove strategy effectiveness |
| v0.5.1-validation-gap-remediation | v0.5.1-validation-gap-remediation | selected validation gap remediation | yes | market-rule-aware execution and generalized PIT schema deferred |
| v0.5.1-system-integrity-and-documentation | v0.5.1-system-integrity-and-documentation | documentation, inventory, smoke, and boundary audits | release candidate | no new trading capability |
