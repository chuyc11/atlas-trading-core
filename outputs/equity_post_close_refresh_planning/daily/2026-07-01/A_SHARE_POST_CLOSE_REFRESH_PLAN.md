# A-Share Post-Close Refresh Plan

- timezone: Asia/Shanghai
- recommended_run_time: 15:45
- public_market_data_only: True
- installs_scheduler: False

## Manual Commands
- `python -m trading_core.cli refresh-a-share-data-freshness --target-as-of-date <YYYY-MM-DD>`
- `python -m trading_core.cli owner-daily-status --as-of-date <YYYY-MM-DD>`

This plan does not install cron, Windows Task Scheduler, startup tasks, or a daemon.
