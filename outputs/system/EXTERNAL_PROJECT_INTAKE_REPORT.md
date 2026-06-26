# External Project Intake Report

- target_version: v0.7.0-external-project-intake-and-a-share-selection-plan
- projects_total: 11
- projects_downloaded: 11
- overall_passed: true
- blocking_reasons: []
- recommended_next_version: v0.7.1-a-share-full-market-data-ingestion

## Projects
| repo | priority | downloaded | license | language | direct import | action |
|---|---|---:|---|---|---:|---|
| AlphaSift | A | true | Apache | Python | false | Use as immediate design reference for scanner, ranking, and saved-run artifacts; do not allow LLM output to authorize trades. |
| qstock | A | true | MIT | Python | false | Use as data and factor-design reference; keep trading-core local persistence, hash, and coverage audit rules. |
| daily_stock_analysis | A | true | MIT | Python | false | Use as owner-readable Chinese daily briefing reference; require local evidence chain for claims. |
| guiwzh/stock | A | true | not_detected | Python | false | Use as scoring-weight reference and extend into LongScore, MidScore, ShortScore, RiskScore, LiquidityScore, and CompositeOpportunityScore. |
| Qlib | B | true | MIT | Python | false | Use for ML and walk-forward evaluation design only; do not pull heavy framework dependencies into v0.7 main flow. |
| AlphaEvo | B | true | Apache | Python | false | Use only for research on Long/Mid/ShortScore weights; require walk-forward validation and never allow automatic trading. |
| zvt | B/C | true | MIT | Python | false | Keep as optional architecture reference; do not import into v0.7 main flow without separate dependency and license review. |
| easytrader | D | true | MIT | Python | false | Use only for future adapter research; v0.7 must not submit orders or manage credentials. |
| easyquotation | D | true | MIT | Python | false | Use as future quote adapter reference; do not feed real-time quotes into formal v0.7 scoring by default. |
| easyquant | D | true | MIT_in_readme | Python | false | Use only as future event-engine and adapter reference; do not connect trading code in v0.7. |
| THSTrader | D | true | GPL | Python | false | Keep outside main flow as experimental_ths_sim_adapter research only. |

## Boundary
- No real trading.
- No broker connection.
- No real orders.
- No third-party trading code merged into the main flow.
- No LLM direct trading decision.
- No model profit guarantee.
- ETF forward dry-run status unchanged.
- `run-daily` not called.
