# A-Share Candidate Generation Audit

- target_version: v0.7.5-a-share-candidate-generation-system
- as_of_date: 2026-06-26
- overall_passed: true
- blocking_reasons: []
- warnings: 0
- counts: {'strict_tradable_count': 3676, 'scored_symbols': 3676, 'long_candidates': 30, 'mid_candidates': 30, 'short_candidates': 30, 'extended_watch_pool': 300, 'multi_horizon_candidates': 50, 'risk_downgraded_candidates': 294}
- forbidden_artifacts: {'virtual_portfolio_artifacts_present': [], 'buy_sell_signal_artifacts_present': [], 'order_preview_artifacts_present': []}

## Boundary
- Candidate generation only.
- Candidates generated: true.
- Watch pools generated: true.
- No virtual portfolios generated.
- No buy/sell signals generated.
- No order preview generated.
- Official forward dry-run status unchanged.
- Day2 was not executed.
- run-daily was not called.
- No broker is connected.
- No real orders were placed.
- This is not a model profit guarantee.
- Live trading ready: false.
- Candidates are not investment advice or trade instructions.

Recommended next version: v0.7.6-a-share-virtual-portfolio-construction
