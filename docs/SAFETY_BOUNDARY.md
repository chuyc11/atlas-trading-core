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

Required interpretations:

- Shadow output is not an order.
- Promotion simulation is not promotion.
- Research report is not an admission gate.
- Historical replay is not forward 30d dry-run.
- Price-only replay is not full global-briefing replay.

Operational rule: if an artifact says `watch`, `shadow`, `promising_shadow`, or `active_small_candidate`, it is still not permission to trade live or change strategy state.
