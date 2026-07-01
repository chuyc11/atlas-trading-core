# A Share v0.9.0 Audit Sweep Plan

v0.9.0 must audit v0.8.13 through v0.8.21 before RC closeout.

Every audit in the sweep is expected to preserve research-only and virtual-only boundaries, with no broker connection, no real orders, no order previews, no trading signals, no old `run-daily`, and no official forward dry-run day2 execution.

The v0.8.21 closeout review audit is:

```powershell
python -m trading_core.cli audit-a-share-owner-closeout-review --as-of-date 2026-06-26
```
