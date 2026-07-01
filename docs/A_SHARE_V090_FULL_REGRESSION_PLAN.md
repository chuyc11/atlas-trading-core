# A Share v0.9.0 Full Regression Plan

v0.8.21 generates this plan but does not execute full pytest.

Required v0.9.0 command:

```powershell
python -m pytest
```

Audit sweep:

- v0.8.13 owner readiness gate audit
- v0.8.14 quality exception workflow audit
- v0.8.15 recovery audit
- v0.8.16 recovery execution audit
- v0.8.17 controlled reevaluation audit
- v0.8.18 recovery evidence audit
- v0.8.19 evidence-backed prep audit
- v0.8.20 gate outcome audit
- v0.8.21 closeout review audit

Boundary scans must cover forbidden artifacts, protected paths, forbidden positive wording, source trace hashes, version/tag/CLI version consistency, release notes completeness, and docs freeze.
