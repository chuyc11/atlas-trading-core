# A Share Recovery Task Evidence

v0.8.16 tracks local recovery task evidence without fabricating completion.

## Evidence Rules

- existing local artifacts may be cited
- missing completion evidence is explicitly recorded as unavailable
- forbidden evidence types such as broker connection, order submission, trade execution, signal generation, or real account checks are rejected
- score improvement is not claimed without audit evidence

Primary artifact:

- `data/equity_owner_readiness_recovery_execution/daily/2026-06-26/recovery_task_evidence_registry.json`
