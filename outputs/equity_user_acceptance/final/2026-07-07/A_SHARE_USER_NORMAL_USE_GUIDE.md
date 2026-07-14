# A 股研究平台用户正常使用指南

当前状态：USER_NORMAL_USE_STATUS = BLOCKED。

本系统只能用于研究、模拟和虚拟环境。仅研究用途；仅模拟用途；仅虚拟环境；不构成投资建议；不构成买卖信号；尚未达到实盘可用状态。

## 可执行的只读命令

```bash
python -m trading_core.cli --version
python -m trading_core.cli owner-daily-status --as-of-date 2026-07-07
```

## 可查看的材料

- v4.0 final owner dashboard
- v4.0 safety and limitations
- v4.0 known limitations
- v4.0 final audit report
- 本次用户验收 evidence 和 final report

## 禁止事项

不得连接 broker，不得读取真实账户，不得生成真实订单，不得生成订单预览，不得将任何输出解释为买卖信号，不得执行 owner-readiness gate 或 controlled gate reevaluation。
