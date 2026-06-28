# Safety Boundary

Trading Core remains a research-only virtual trading system.

Forbidden actions:

- broker connection
- live order
- live trading
- margin
- short
- futures
- options
- leverage
- automatic promotion
- RL active trading
- LLM trading decision
- using labels in run-daily
- treating shadow as active
- treating A-share workflow orchestration as a broker workflow

Required interpretations:

- Shadow output is not an order.
- Promotion simulation is not promotion.
- Research report is not an admission gate.
- Historical replay is not forward 30d dry-run.
- Price-only replay is not full global-briefing replay.
- A-share daily workflow orchestration is not live trading readiness.
- A-share daily workflow orchestration is not permission to call old run-daily, execute official forward dry-run day2, connect a broker, place real orders, generate buy/sell signals, or generate order previews.

Operational rule: if an artifact says `watch`, `shadow`, `promising_shadow`, or `active_small_candidate`, it is still not permission to trade live or change strategy state.
