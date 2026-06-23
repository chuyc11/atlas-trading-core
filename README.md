# Trading Core

Trading Core is a file-backed virtual trading research system that connects to
the existing `work/global-briefing` workflow through JSON, JSONL, YAML, and
Markdown files.

Implemented first-stage scope:

- File-backed config, storage, JSONL, and schema validation.
- ETF universe, market rules, cost model, virtual account, ledger, positions,
  valuation, risk checks, and T+1 availability.
- Macro signal loading, trading signal generation, virtual orders/trades,
  benchmark comparison, attribution, signal scoring, mistake classification,
  strategy scoring, rule memory, experiment queue, shadow runner, and promotion
  recommendations.
- Daily Markdown report, `run-daily`, global-briefing file integration,
  event-driven T+1 backtest, and walk-forward summaries.

Safety boundary:

- No broker connection.
- No real orders.
- No live trading.
- No margin, shorting, options, futures, or leverage.

## Verify

From this directory:

```powershell
python -m trading_core.cli --help
python -m pytest
python -m trading_core.cli run-daily --date 2026-06-23
python -m trading_core.cli backtest --start-date 2026-06-23 --end-date 2026-06-24
python -m trading_core.cli walk-forward --start-date 2026-06-23 --end-date 2026-06-24 --window-days 1
```

`pytest` covers the first-stage modules end to end, including synthetic BUY,
trade, T+1 settlement, benchmark, attribution, evolution, daily report,
global-briefing missing-file fallback, T+1 event backtest, and walk-forward.
