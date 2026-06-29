# A-Share Gated Build Runbook

Run the release E2E:

```bash
python -m trading_core.cli validate-a-share-gated-build-inputs --as-of-date 2026-06-26
python -m trading_core.cli build-a-share-gated-build-from-existing-data --as-of-date 2026-06-26 --mode run_gated_build_from_existing_data
python -m trading_core.cli audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26
```

Or:

```bash
python -m trading_core.cli build-and-audit-a-share-gated-build-from-existing-data --as-of-date 2026-06-26 --mode run_gated_build_from_existing_data
```

Do not pass broker/order/live-trading flags. Do not use public refresh or `full_research_run` for this stage.

