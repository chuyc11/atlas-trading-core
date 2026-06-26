# External Project Reuse Matrix

| repo | priority | patterns to reuse | action | direct import allowed |
|---|---|---|---|---:|
| AlphaSift | A | full-market scanner, hard filters, factor scoring, candidate ranking schema, T+N evaluation schema, saved run artifacts | Use as immediate design reference for scanner, ranking, and saved-run artifacts; do not allow LLM output to authorize trades. | false |
| qstock | A | data adapter, public screening condition expression, RPS indicator, MM trend model, fundamental fields, capital flow fields | Use as data and factor-design reference; keep trading-core local persistence, hash, and coverage audit rules. | false |
| daily_stock_analysis | A | daily briefing structure, LLM report prompt, multi-market report layout, notification workflow, news risk note | Use as owner-readable Chinese daily briefing reference; require local evidence chain for claims. | false |
| guiwzh/stock | A | short score weights, long score weights, value/technical/valuation scoring, readable stock score report | Use as scoring-weight reference and extend into LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, and CompositeOpportunityScore. | false |
| Qlib | B | dataset split, model training workflow, backtest evaluation metrics, RankIC/IC evaluation, portfolio analysis report, experiment tracking | Use for ML and walk-forward evaluation design only; do not pull heavy framework dependencies into v0.7 main flow. | false |
| AlphaEvo | B | controlled mutation, scoring weight optimization, strategy evolution report, parameter evidence chain, failed strategy diagnosis | Use only for research on Long/Mid/ShortScore weights; require walk-forward validation and never allow automatic trading. | false |
| zvt | B/C | data domain modeling, factor pipeline, research framework organization | Keep as optional architecture reference; do not import into v0.7 main flow without separate dependency and license review. | false |
| easytrader | D | broker adapter interface, miniQMT adapter, client automation separation, order preview to submit layering, read-only account sync | Use only for future adapter research; v0.7 must not submit orders or manage credentials. | false |
| easyquotation | D | quote adapter, quote normalization, watchlist polling, field standardization | Use as future quote adapter reference; do not feed real-time quotes into formal v0.7 scoring by default. | false |
| easyquant | D | event engine, quotation/trader separation, strategy event loop, simulated trading flow | Use only as future event-engine and adapter reference; do not connect trading code in v0.7. | false |
| THSTrader | D | THS simulated trading flow, Android emulator/app automation, simulated order submit adapter | Keep outside main flow as experimental_ths_sim_adapter research only. | false |

## Integration Rule

Do not merge third-party trading code into the main flow. All reuse must pass separate license, dependency, data reproducibility, and boundary review.
