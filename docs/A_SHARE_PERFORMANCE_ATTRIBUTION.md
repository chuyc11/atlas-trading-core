# A-Share Performance Attribution

v0.7.12 adds research-only A-share virtual portfolio performance attribution and risk diagnostics.

It generates structural diagnostics for the existing long/mid/short virtual portfolios:

- holding contribution snapshot
- industry contribution snapshot
- candidate-source contribution snapshot
- score, risk, and liquidity bucket contribution snapshots
- benchmark-relative structural attribution
- concentration, risk, liquidity, industry, and factor exposure diagnostics
- attribution limitations, source trace, manifest, boundary check, summary, and audit

Current v0.7.12 history is limited to the available v0.7.11 portfolio observations. For `2026-06-26`, realized multi-day attribution is not available, and outputs are primarily structural exposure diagnostics.

Boundary:

- v0.7.12 does not create buy/sell signals
- v0.7.12 does not place orders
- v0.7.12 does not connect broker
- v0.7.12 does not call old run-daily
- v0.7.12 does not execute official forward dry-run day2
- v0.7.12 does not fabricate performance
- v0.7.12 distinguishes structural diagnostics from realized performance attribution

v0.8.0 adds daily data refresh and provider hardening without changing attribution outputs into trading instructions.

v0.8.2 reads attribution summary and audit artifacts into the owner dashboard. It displays structural diagnostics and limited-history status only. It does not upgrade attribution into realized strategy proof, trading advice, broker readiness, or live-trading readiness.

Recommended next version: `v0.8.3-a-share-owner-alerting-and-run-history-monitoring`.
