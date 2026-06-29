# A-Share Current-Day Runbook

Validate readiness only:

```bash
python -m trading_core.cli validate-a-share-current-day-readiness --as-of-date 2026-06-26
```

Run from existing refresh:

```bash
python -m trading_core.cli run-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
```

Run and audit:

```bash
python -m trading_core.cli run-and-audit-a-share-current-day-research --as-of-date 2026-06-26 --mode run_research_from_existing_refresh --workflow-mode validate_existing_artifacts
```

Operational notes:

- data refresh audit must pass before workflow execution
- release mode does not require public network provider success
- `refresh_then_run_research` requires `--allow-refresh-before-run`
- public providers require both `--allow-network-providers` and `--allow-public-providers`
- post-workflow benchmark/performance/attribution modules are opt-in with `--run-post-workflow-modules`
- current-day research output is not a trade instruction

