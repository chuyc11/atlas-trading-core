# A Share Build Output Ops Refresh Schema

The v0.8.10 package includes config, input availability, source resolution, date alignment, monitoring refresh, alert summary refresh, remediation refresh, safe action refresh, ops center refresh, ops history refresh, health score refresh, module status matrix refresh, issue summary refresh, action summary refresh, owner next steps refresh, original-vs-build-output comparison, artifact navigation, source trace, boundary, manifest, and summary.

Required invariants:

- `source_workflow_mode=build_from_existing_data`
- `business_output_drift_count=0`
- `protected_path_modifications_detected=false`
- `build_from_existing_data_rerun=false`
- `execute_remediation_actions=false`
- `external_notifications_sent=false`
- `automatic_action_count=0`

