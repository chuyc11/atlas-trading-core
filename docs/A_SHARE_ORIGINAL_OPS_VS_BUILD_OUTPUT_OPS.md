# A Share Original Ops vs Build Output Ops

v0.8.10 compares original monitoring/remediation/ops artifacts with the build-output ops refresh.

Expected differences are source-mode differences: original ops artifacts came from earlier validate-source/current-day layers, while build-output ops refresh uses the verified `build_from_existing_data` dashboard as primary source.

Unexpected differences include changed health score, changed automatic action count, blocking issue drift, or boundary drift. Unexpected differences are blocking in the audit.

