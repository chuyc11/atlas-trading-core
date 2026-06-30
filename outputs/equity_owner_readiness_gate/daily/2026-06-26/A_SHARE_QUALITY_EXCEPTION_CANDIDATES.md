# A Share Quality Exception Candidates

- Candidate exceptions are not approvals or waivers.
- candidate_count: 3
- auto_waiver_allowed: False

- owner_readiness_score_gate: blocking / owner_readiness_score_below_threshold / auto_waiver_allowed=False
- warning_issue_quality_gate: warning / warning_issue_items_present / auto_waiver_allowed=False
- trend_sufficiency_quality_gate: warning / insufficient_history_correctly_flagged / auto_waiver_allowed=False
