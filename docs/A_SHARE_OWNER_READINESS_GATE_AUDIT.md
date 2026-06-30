# A Share Owner Readiness Gate Audit

The v0.8.13 audit command is:

```powershell
python -m trading_core.cli audit-a-share-owner-readiness-gate --as-of-date 2026-06-26
```

The audit checks required artifacts, upstream audit pass state, threshold policy application, gate decision consistency, correct blocked-state representation, absence of automatic waivers, source trace completeness, boundary cleanliness, forbidden wording, and forbidden artifacts.

An audit can pass when the gate decision is `blocked`, as long as the blocked state is represented correctly and no unsafe action occurred.
