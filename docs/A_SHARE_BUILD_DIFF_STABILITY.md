# A-Share Build Diff Stability

v0.8.8 classifies build-vs-build differences into:

- `no_drift`
- `timestamp_only_drift`
- `metadata_hash_drift`
- `business_output_drift`
- `missing_required_artifact`
- `new_expected_artifact`
- `unexpected_artifact`
- `boundary_drift`
- `protected_path_drift`
- `source_trace_drift`

Timestamp-only drift is non-blocking. Metadata/hash drift is non-blocking when normalized business content is stable. Business output drift is blocking by default. Missing required artifacts, boundary drift, protected path drift, and source trace drift are blocking.

