# A Share Owner Readiness Gate Schema

Primary v0.8.13 data directory:

`data/equity_owner_readiness_gate/daily/YYYY-MM-DD/`

Required artifact groups:

- config, input availability, source resolution, and date alignment
- owner readiness threshold policy and daily pack quality threshold policy
- score, completeness, warning/issue, safe action, protected path, boundary, source trace, trend sufficiency, markdown report, artifact navigation, and owner next-step gates
- owner readiness gate decision
- quality threshold evaluation
- quality exception candidate list
- owner release recommendation
- source trace, boundary check, manifest, and summary

Gate artifacts include `gate_id`, `as_of_date`, `source_workflow_mode`, `threshold`, `actual_value`, `passed`, `blocking_reasons`, `warnings`, `source_artifacts`, and `interpretation_zh`.
