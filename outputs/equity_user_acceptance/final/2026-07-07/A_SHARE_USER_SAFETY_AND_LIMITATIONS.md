# A 股用户验收安全边界与限制

本验收确认以下边界保持不变：

- research_only = true
- simulation_only = true
- virtual_only = true
- not_real_order = true
- not_order_preview = true
- not_buy_sell_signal = true
- not_investment_advice = true
- not_live_trading_ready = true
- broker_connected = false
- real_account_data_read = false
- real_orders_placed = false
- real_order_preview_generated = false
- buy_sell_signals_generated = false
- owner_readiness_gate_rerun = false
- controlled_gate_reevaluation_run = false
- new_gate_score_generated = false
- new_gate_decision_generated = false

## 用户可读限制

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
