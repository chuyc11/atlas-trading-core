# A 股最终用户验收测试证据

## Baseline

- git clean before acceptance: true
- VERSION: v4.0.0-a-share-research-platform-final-maintenance-closeout-and-freeze
- CLI version: trading-core 4.0.0
- release tag exists: true
- pre-acceptance quarantine stash: `stash@{1}`
- workflow side-effect quarantine stash: `stash@{0}`

## CLI Smoke

- `python -m trading_core.cli --version`: passed
- `owner-daily-status --as-of-date 2026-07-07`: passed
- v4.0 build/audit/build-and-audit/help smoke: passed
- v4.0.1 maintenance polish commands: not present
- legacy forbidden CLI names detected: true

## Regression

- semantic regression: 16 passed, 0 failed
- owner/v4.0 targeted tests: 17 passed
- full regression single command: timeout after 904 seconds
- split matrix: 2096 passed, 1 skipped, 3 failed
- failed file: `tests/test_a_share_v31_post_v3_verification.py`

## Safety

All broker/account/order/order-preview/buy-sell/live-trading flags remained false. owner-readiness gate rerun and controlled gate reevaluation were not executed.
