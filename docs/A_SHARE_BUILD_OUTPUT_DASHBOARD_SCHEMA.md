# A-Share Build Output Dashboard Schema

Required artifacts:

- `build_output_dashboard_config.json`
- `build_output_input_availability.json`
- `build_output_source_resolution.json`
- `build_output_date_alignment.json`
- `build_output_executive_status_card.json`
- `build_output_data_freshness_card.json`
- `build_output_workflow_status_card.json`
- `build_output_research_output_card.json`
- `build_output_candidate_summary_card.json`
- `build_output_portfolio_summary_card.json`
- `build_output_benchmark_summary_card.json`
- `build_output_performance_summary_card.json`
- `build_output_attribution_summary_card.json`
- `build_output_repeatability_card.json`
- `build_output_protected_path_card.json`
- `build_output_warning_and_blocker_card.json`
- `build_output_artifact_navigation.json`
- `validate_dashboard_vs_build_dashboard_comparison.json`
- `build_output_dashboard_source_trace.json`
- `build_output_dashboard_boundary_check.json`
- `build_output_dashboard_manifest.json`
- `build_output_dashboard_summary.json`

The config fixes `source_workflow_mode=build_from_existing_data`, `prefer_build_output=true`, `allow_validate_fallback_for_required_artifacts=false`, `require_repeatability_audit_passed=true`, `require_business_output_drift_count_zero=true`, and `require_protected_path_modification_clean=true`.

