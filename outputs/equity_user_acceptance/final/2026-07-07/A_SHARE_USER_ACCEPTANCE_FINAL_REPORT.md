# A 股研究平台最终用户验收报告

## 1. 结论

USER_NORMAL_USE_STATUS = BLOCKED

overall_passed = false

## 2. 本结论代表什么

本次验收确认系统仍保持 research-only / simulation-only / virtual-only 的安全边界，但当前冻结线不能判定为普通用户可正常使用。阻断项来自 owner-facing 报告可读性、known limitations 枚举、full regression 失败，以及 targeted user acceptance tests 缺失。

## 3. 本结论不代表什么

本结论不代表实盘可用，不代表投资建议，不代表买卖信号，不代表真实账户或真实订单能力。系统不得连接 broker，不得读取真实账户，不得生成真实订单，不得生成订单预览。

## 4. 测试范围

覆盖 CLI smoke、owner-daily-status、final owner dashboard、v4.0 final audit、reports、artifacts、semantic regression、split-matrix full regression、safety boundary、protected paths、known limitations 和用户正常使用路径。

## 5. 测试结果

- baseline hygiene: PASSED；dirty v40 2026-07-07 生成物已通过 path-limited stash 隔离。
- CLI version: trading-core 4.0.0；VERSION: v4.0.0-a-share-research-platform-final-maintenance-closeout-and-freeze。
- owner-daily-status: PASSED；owner_readiness_state=blocked，owner_operationally_acceptable=false。
- v4.0 dashboard CLI: PASSED；写入 v40 release artifact side effects，已 quarantine。
- v4.0 audit CLI: PASSED；overall_passed=true，blocking_reasons=[]。
- report readability: FAILED；v4.0 Markdown 仍是 raw key-value dump，标题包含 A Share V40，缺少中文免责声明。
- known limitations: FAILED；未提供 >=20 条用户可读限制清单。
- semantic regression: PASSED；16 passed，0 failed。
- full regression: FAILED；single-command pytest 904 秒超时，split matrix 2096 passed / 1 skipped / 3 failed。
- artifact integrity: PASSED；未发现历史、审计、发布证据被删除。
- protected paths: PASSED；历史 data/orders 和 data/trades 存在，但本次验收未修改。
- safety boundary: PASSED；broker/account/order/order-preview/buy-sell/live-trading flags 均保持 false。

## 6. 用户正常使用路径

当前不应按 READY 状态交付给普通用户。可以安全查看以下只读材料和命令：

- `python -m trading_core.cli owner-daily-status --as-of-date 2026-07-07`
- `outputs/equity_v40_final_maintenance_closeout/daily/2026-07-01/A_SHARE_V40_OWNER_FINAL_MAINTENANCE_DASHBOARD.md`
- `outputs/equity_v40_final_maintenance_closeout/daily/2026-07-01/A_SHARE_V40_KNOWN_LIMITATIONS_FINAL.md`
- `outputs/equity_v40_final_maintenance_closeout/daily/2026-07-01/A_SHARE_V40_SAFETY_AND_LIMITATIONS.md`
- `outputs/audit/A_SHARE_V40_FINAL_MAINTENANCE_CLOSEOUT_AUDIT.md`

## 7. 已知限制

1. 仅研究用途，不代表生产交易系统。
2. 仅模拟用途，不代表真实交易授权。
3. 仅虚拟环境，不接入真实券商环境。
4. 不接 broker。
5. 不读取真实账户。
6. 不生成真实订单。
7. 不生成订单预览。
8. 不生成买卖信号。
9. 不构成投资建议。
10. 尚未达到实盘可用状态。
11. owner-readiness 当前为 blocked。
12. full regression 本次使用 split matrix。
13. single-command pytest 受本地 Windows/timeout 限制未完成。
14. benchmark claims 依赖 benchmark source。
15. financial PIT claims 依赖 visible/announcement date。
16. portfolio attribution 仅为模拟。
17. canary 仅为 virtual-only。
18. LLM/RL 不能授权交易。
19. knowledge base 不能回答买入、卖出或配置比例。
20. incident drill/recovery rehearsal 仅为 dry-run。

## 8. 阻断项

- owner_report_unreadable：owner-facing v4.0 Markdown 仍是 raw key-value dump。
- known_limitations_not_enumerated：known limitations 未按用户可读方式枚举 >=20 条。
- full_regression_failed：chunk 9 中 `tests/test_a_share_v31_post_v3_verification.py` 有 3 个失败。
- targeted_user_acceptance_tests_missing：`tests/test_a_share_user_acceptance*.py` 不存在；本轮禁止修改 tests，未新增。
- legacy_forbidden_cli_names_exposed：全局 CLI 仍暴露 legacy signal/order/order-preview/owner gate 命令名。
- dirty_worktree_after_acceptance：最终 git status 包含本次生成的用户验收 artifacts 和用户验收 audit artifacts。

## 9. 后续建议

recommended_next_version = maintenance-only

后续只应做 maintenance-only 修复：改善 owner-facing 中文报告、枚举 known limitations、处理 v31 regression failure，并补齐 user acceptance tests。不得修改交易语义，不得接 broker，不得生成真实订单或订单预览，不得生成买卖信号，不得重跑 owner-readiness gate。
