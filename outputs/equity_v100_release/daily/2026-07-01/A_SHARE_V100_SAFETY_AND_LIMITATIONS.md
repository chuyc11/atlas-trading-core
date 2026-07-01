# A股 v1.0.0 安全边界与限制

## 1. Safety Boundary
- The v1.0.0 platform is released as research-only and simulation-only. It supports autonomous research, automated experiments, RL simulation, virtual broker, paper ledger, shadow/canary simulation, and simulated strategy promotion. It does not support real broker connection, real account reading, real order placement, real order preview, or real buy/sell signals. Owner-readiness remains blocked. This release is not live trading ready.

## 2. Simulation-Only Execution
- 所有订单意图、成交、账户、ledger、实验和晋级均为模拟用途。

## 3. No Real Broker / No Real Account / No Real Orders
- 不连接真实 broker，不读取真实账户，不下真实订单。

## 4. No Buy/Sell Signals
- 任何模拟动作都不是买卖信号，也不能复制到真实账户执行。

## 5. Owner-Readiness Still Blocked
- owner-readiness 仍为 blocked：54 / 75 / gap 21。

## 6. Benchmark Warning and Performance Claim Limitation
- benchmark/index attribution source 缺失或不完整，阻止真实绩效宣称。

## 7. What Users Must Not Do
- 不要连接 broker、读取真实账户、下单、生成订单预览、把模拟动作当作买卖建议或实盘指令。

## 8. Future Hardening
- 下一步建议：v1.0.1-a-share-benchmark-data-and-performance-claim-hardening
