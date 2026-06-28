# A-Share Attribution Interpretation

v0.7.12 attribution outputs should be read as structural diagnostics until enough forward observations exist.

For the current `2026-06-26` baseline:

- structural diagnostics are available
- realized multi-day performance attribution is not available
- first-day initialization is not strategy effectiveness evidence
- benchmark-relative exposure is structural where benchmark constituents are available
- CSI index return data exists, but constituent exposure is not fabricated

Do not interpret score, risk, liquidity, industry, or benchmark-relative diagnostics as trade instructions. These artifacts explain the current virtual portfolio shape and risk exposures.

v0.8.0 adds daily data refresh and provider hardening. It validates data freshness and coverage, but does not generate buy/sell signals, place orders, connect broker, call old `run-daily`, or execute official forward dry-run day2.

Recommended next version: `v0.8.1-a-share-current-day-research-workflow-runner`.
