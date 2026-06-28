# A-Share Attribution Audit

Audit command:

```bash
python -m trading_core.cli audit-a-share-performance-attribution --as-of-date 2026-06-26
```

Combined build and audit command:

```bash
python -m trading_core.cli build-and-audit-a-share-performance-attribution --as-of-date 2026-06-26
```

The audit verifies:

- all attribution artifacts exist
- all required portfolio ids and benchmark ids are present
- limited history is correctly flagged
- realized performance attribution is not fabricated
- structural diagnostics are available
- holding, industry, score bucket, risk bucket, and liquidity bucket weights reconcile
- `risk_downgraded_symbols_in_portfolio=[]`
- `excluded_universe_exposure=0`
- source trace is complete and hashes match where applicable
- boundary fields remain clean

v0.7.12 does not create buy/sell signals, place orders, connect broker, call old run-daily, execute official forward dry-run day2, or claim live trading readiness.
