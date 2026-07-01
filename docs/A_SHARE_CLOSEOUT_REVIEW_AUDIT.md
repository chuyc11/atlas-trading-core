# A Share Closeout Review Audit

Audit command:

```powershell
python -m trading_core.cli audit-a-share-owner-closeout-review --as-of-date 2026-06-26
```

Current result:

- audit_id=`A-SHARE-OWNER-CLOSEOUT-REVIEW-AUDIT`
- overall_passed=true
- blocking_reasons=[]
- v0820_outcome_audit_passed=true
- selected_v0820_branch=`final_blocked_closeout`
- source_gate_decision=`blocked`
- blocked_state_lineage_represented=true
- readiness_score_lineage_represented=true
- score_gap_represented=true
- new_gate_score_generated=false
- new_gate_decision_generated=false
- full_pytest_executed=false
- v090_full_regression_plan_generated=true
- v090_audit_sweep_plan_generated=true
- v090_rc_decision_consistent=true
