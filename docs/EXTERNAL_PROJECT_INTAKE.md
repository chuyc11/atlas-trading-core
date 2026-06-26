# External Project Intake

This document summarizes downloaded external repositories for design reference only.

| repo | use | priority | risk | usable modules |
|---|---|---|---|---|
| AlphaSift | full-market scanning, multi-factor candidate ranking, risk-aware scoring, saved-run evaluation | A | medium | README.md, strategies/ |
| qstock | A-share public data adapters, WenCai-style screening, RPS, MM trend, fundamentals, capital flow, visualization | A | medium_high | README.md |
| daily_stock_analysis | daily stock analysis reports, LLM summaries, market/news organization, notification ideas | A | medium | README.md, docs/, main.py |
| guiwzh/stock | A-share stock scoring assistant with short/long score weighting and value/technical/valuation dimensions | A | medium | README.md |
| Qlib | ML quant research workflow, dataset split, model evaluation, RankIC/IC, portfolio evaluation | B | high | README.md, examples/, qlib/contrib/, qlib/workflow/, qlib/backtest/, qlib/model/ |
| AlphaEvo | strategy weight mutation, controlled optimization, evolution report, failed strategy diagnosis | B | medium_high | README.md, strategies/ |
| zvt | market data, factor, and quant research framework reference | B/C | high | README.md, src/, examples/ |
| easytrader | broker/client adapter reference, miniQMT, Xueqiu portfolio, future order-submit layering | D | high | README.md, easytrader/, easytrader/clienttrader.py, easytrader/xqtrader.py |
| easyquotation | free quote adapters and quote normalization reference | D | medium_high | README.md, easyquotation/ |
| easyquant | event engine and quotation/trader layering reference | D | high | README.md, easyquant/ |
| THSTrader | Tonghuashun simulated trading automation research | D | high | README.md |

## Boundary
- No real trading.
- No broker connection.
- No real orders.
- No third-party trading code merged into the main flow.
- No LLM direct trading decision.
- No model profit guarantee.
- ETF forward dry-run status unchanged.
- `run-daily` not called.
