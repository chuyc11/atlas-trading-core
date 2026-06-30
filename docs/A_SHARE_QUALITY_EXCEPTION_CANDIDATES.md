# A Share Quality Exception Candidates

v0.8.13 generates quality exception candidates when gates produce blocking reasons or warnings.

These candidates are not waiver approvals. Automatic waiver is always disabled in v0.8.13. Actual exception approval, waiver records, escalation workflow, and owner follow-up tracking are deferred to v0.8.14.

Each candidate is non-trading, non-broker, and non-order related.

v0.8.14 materializes these candidates into a registry, classification, waiver candidate evaluation, escalation workflow, owner notice, and developer follow-up tracker. The default waiver decision remains `not_requested`.
