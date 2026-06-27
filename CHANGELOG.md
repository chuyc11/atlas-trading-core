# Changelog

## v0.7.3-a-share-multi-horizon-feature-engineering

- Added strict-universe A-share short, mid, long, risk, liquidity, industry, and fundamental feature artifacts.
- Added feature manifest, field coverage, generation summary, reports, and fail-closed audit.
- Added CLI commands for build, audit, and build-and-audit feature generation.
- Verified the stage remains feature-only: no scores, candidates, watchlists, virtual portfolios, broker calls, real orders, run-daily, profit claims, or live-trading readiness.

## v0.1.0-core-hardened

- Completed Issue 1-31 for the file-backed virtual trading core.
- Added hardened acceptance tests, runtime health, historical ETF backtest support, admission gate, trading summary export, and evolution throttling.
- Verified no broker connection, no live trading, no ML/RL/LLM trading decision path.
- Completed Issue 1-36 for the file-backed virtual trading research base.
- Baseline validation: 83 tests passed at v0.1.0-core-hardened freeze.
