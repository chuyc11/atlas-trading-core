# Architecture

Trading Core is a file-backed research system. Each layer writes explicit artifacts and keeps the live-trading boundary closed.

| Layer | Inputs | Outputs | Main modules | Write main ledger | Affects run-daily |
|---|---|---|---|---|---|
| data acquisition | external price files, configured symbols | `data/raw/`, fetched price manifests | `trading_core.data.historical_prices`, `trading_core.data.price_acquisition`, `trading_core.data.price_dataset_merge` | no | no |
| data validation | raw and merged datasets | validation JSON/Markdown | `trading_core.data.data_package_validator`, `trading_core.evaluation.real_data_validation_report` | no | no |
| trading core | macro signals, prices, account snapshots | virtual signals, orders, trades, portfolios, daily reports | `trading_core.daily_run`, `trading_core.signals`, `trading_core.risk`, `trading_core.broker`, `trading_core.accounting` | yes, only for virtual file-backed daily workflow | yes, this is the daily workflow |
| backtest / replay | historical price datasets, strategies | `data/backtests/`, `data/replays/`, `outputs/backtests/`, `outputs/replays/` | `trading_core.backtest`, `trading_core.evaluation.historical_dry_run_replay` | no unless explicitly requested for replay, default is no | no |
| ML shadow | feature and label artifacts | `data/ml/`, `data/shadow/`, `outputs/ml/`, `outputs/shadow/` | `trading_core.features`, `trading_core.labels`, `trading_core.ml` | no | no |
| experiment system | registry configs, sweep outputs, shadow outputs | `data/experiments/`, `outputs/experiments/` | `trading_core.experiments` | no | no |
| reporting control plane | existing research artifacts | `data/reports/`, `data/system/`, `outputs/reports/`, `outputs/system/` | `trading_core.reports` | no | no |
| audits | docs, code, generated artifacts | `data/system/`, `outputs/audit/` | `trading_core.system`, audit modules under `trading_core.experiments` and `trading_core.reports` | no | no |

The daily workflow remains virtual and file-backed. Research layers do not promote strategies, do not call a broker, and do not write the main virtual ledger.
