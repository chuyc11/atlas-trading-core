# A Share Quality Exception Workflow Audit

Run:

```powershell
python -m trading_core.cli audit-a-share-owner-quality-exceptions --as-of-date 2026-06-26
```

The audit checks required artifacts, input owner readiness gate audit status, blocked decision preservation, readiness score gap, exception classification, waiver controls, escalation routes, follow-up commands, source trace, boundary cleanliness, forbidden artifacts, and forbidden positive wording.

The audit passes only when the blocked gate decision remains preserved and no automatic waiver or unsafe action is introduced.
