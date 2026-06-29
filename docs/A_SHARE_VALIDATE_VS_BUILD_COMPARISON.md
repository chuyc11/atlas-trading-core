# A-Share Validate Vs Build Comparison

v0.8.7 compares the prior `validate_existing_artifacts` current-day package with the gated `build_from_existing_data` run.

The comparison records:

- workflow mode difference
- audit status comparison
- stage status comparison
- artifact existence comparison
- boundary comparison
- warning comparison
- source trace comparison
- business output drift
- timestamp-only drift
- hash-only drift
- missing required artifacts

Timestamp metadata drift is non-blocking. Missing required artifacts and boundary drift are blocking.

