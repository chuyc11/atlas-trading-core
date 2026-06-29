# A 股 Repeatability Source Trace

- 日期: 2026-06-26
- source_trace_complete: True
- forbidden_generated_sources: []

## Boundary Assumptions

- repeatability_only=True
- research_only=True
- virtual_only=True
- preexisting protected paths are allowed only if unchanged
- no broker connection
- no real orders
- no order preview
- no buy/sell signals
- no old run-daily call
- no official forward dry-run day2

## Entries

- gated_build_audit: exists=True sha256=64f0bcbff5cf
- gated_build_manifest: exists=True sha256=0fbb9373eb67
- gated_build_execution_record: exists=True sha256=a2f7012770de
- gated_build_workflow_result: exists=True sha256=eee5ae7780f6
- gated_build_artifact_drift: exists=True sha256=bf55c30b938c
- gated_build_boundary_check: exists=True sha256=b583cefc3db0
- ops_history_audit: exists=True sha256=a25861899e74
- ops_center_audit: exists=True sha256=a8aad875bb2a
- data_refresh_audit: exists=True sha256=6fda172e7592
- current_day_audit: exists=True sha256=2fd7c7ac4377
- repeatability_config: exists=True sha256=04693b843818
- repeatability_input_availability: exists=True sha256=7185b96177e0
- repeatability_date_alignment: exists=True sha256=66b7e61ea751
- protected_path_pre_run_snapshot: exists=True sha256=9dacd662e116
- repeat_build_execution_plan: exists=True sha256=72a18fc74cbd
- repeat_build_execution_record: exists=True sha256=6845e97eb064
- repeat_build_workflow_result: exists=True sha256=d3edfb391337
- protected_path_post_run_snapshot: exists=True sha256=e3ea0cd1d955
- protected_path_modification_check: exists=True sha256=db44c34645ea
- first_build_artifact_snapshot: exists=True sha256=d3d5b1fb27b6
- second_build_artifact_snapshot: exists=True sha256=52b1436319e7
- build_vs_build_comparison: exists=True sha256=2b6a1d32acf7
- repeatability_drift_summary: exists=True sha256=dfd035308b5f
- deterministic_field_normalization: exists=True sha256=8d8e7bda7772
- repeatability_warning_comparison: exists=True sha256=77278ca24181
- repeatability_source_trace: exists=True sha256=18fe8d0f6b88
- repeatability_boundary_check: exists=True sha256=5c09a2009ca5
- repeatability_manifest: exists=True sha256=47672602a2bb
- repeatability_summary: exists=True sha256=553d491cc857
