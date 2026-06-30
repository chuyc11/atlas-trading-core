# A Share Owner Quality Exception Workflow

v0.8.14 adds daily pack quality exception and escalation workflow.

The workflow reads v0.8.13 owner readiness gate artifacts and preserves the blocked gate decision. It explains why the audit can pass while the gate remains blocked, classifies quality exceptions, creates manual waiver schema, routes escalation, and creates owner/developer follow-up artifacts.

It does not auto-waive quality gates and does not change the v0.8.13 gate decision.
