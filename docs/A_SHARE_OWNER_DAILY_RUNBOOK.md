# A-Share Owner Daily Runbook

The v0.8.11 daily runbook is generated at:

- `data/equity_owner_daily_pack/daily/YYYY-MM-DD/owner_daily_runbook.json`
- `outputs/equity_owner_daily_pack/daily/YYYY-MM-DD/A_SHARE_OWNER_DAILY_RUNBOOK.md`

The runbook gives the owner a safe daily review sequence:

1. Open the daily status brief.
2. Check the build-output dashboard.
3. Check monitoring, remediation, and ops refresh.
4. Check warning, issue, and safe-action digests.
5. Check protected path status.
6. Check source trace and boundary.
7. Read the research output digest.
8. Record owner notes.
9. Decide whether developer follow-up is needed.
10. Confirm no trading action is executed.

The only command references are audit-only commands. The runbook does not execute commands, does not execute remediation actions, does not send notifications, does not connect broker, does not place orders, and does not generate order previews or buy/sell signals.
