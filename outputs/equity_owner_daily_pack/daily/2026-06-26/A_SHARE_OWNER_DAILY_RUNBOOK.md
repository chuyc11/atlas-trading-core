# A 股 Owner Daily Runbook

## Daily Review Sequence

1. 打开每日状态简报
2. 检查 build-output dashboard
3. 检查 monitoring / remediation / ops refresh
4. 检查 warning / issue / safe action
5. 检查 protected path 状态
6. 检查 source trace 和 boundary
7. 阅读 research output digest
8. 记录 owner notes
9. 判断是否需要 developer follow-up
10. 确认不执行任何交易动作

## Safe Audit-only Commands

- `python -m trading_core.cli audit-a-share-build-output-owner-dashboard --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-build-output-ops-refresh --as-of-date 2026-06-26`
- `python -m trading_core.cli audit-a-share-owner-daily-pack --as-of-date 2026-06-26`

## Manual Review Checklist

- 确认所有 audit 仍为 passed
- 确认 warning / issue 已分类
- 确认 safe action 均为人工复核
- 确认 protected path 无修改
- 确认 boundary clean

## Developer Escalation Conditions

- blocking_count > 0
- source_trace incomplete
- boundary not clean

## Known Non-blocking Items

- metadata_hash_drift_non_blocking
- timestamp_only_drift_non_blocking

## What Not To Do

- do not connect broker
- do not read real account
- do not place real orders
- do not generate order preview
- do not call old run-daily
