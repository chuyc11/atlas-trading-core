# Testing Policy

## v0.8.17 Targeted Test Policy

For `v0.8.17-a-share-owner-readiness-controlled-gate-reevaluation`, the required validation is targeted pytest only:

```bash
python -m pytest tests/test_a_share_owner_readiness_controlled_gate_reevaluation*.py tests/test_a_share_controlled_gate_reevaluation*.py
```

On Windows PowerShell, expand the same targeted file set before invoking pytest:

```powershell
$tests = @(Get-ChildItem tests -Filter 'test_a_share_owner_readiness_controlled_gate_reevaluation*.py') + @(Get-ChildItem tests -Filter 'test_a_share_controlled_gate_reevaluation*.py')
python -m pytest @($tests.FullName)
```

The v0.8.17 release report must include:

- `full_pytest_run=false`
- `targeted_pytest_passed=true`
- `targeted_pytest_count=<actual>`
- `full_pytest_deferred_until=v0.9.0 or next big-version closeout`

Full pytest is deferred until `v0.9.0` or the next big-version closeout unless explicitly requested.

## v0.8.18 Targeted Test Policy

For `v0.8.18-a-share-recovery-evidence-collection-and-readiness-improvement-artifacts`, use targeted pytest only:

```powershell
$patterns = @('test_a_share_owner_recovery_evidence*.py','test_a_share_recovery_task_evidence_collection.py','test_a_share_developer_follow_up_evidence_package.py','test_a_share_owner_follow_up_evidence_package.py','test_a_share_quality_issue_evidence_package.py','test_a_share_warning_mapping_evidence_package.py','test_a_share_source_trace_improvement_evidence.py','test_a_share_markdown_quality_improvement_evidence.py','test_a_share_artifact_completeness_evidence.py','test_a_share_readiness_improvement_evidence_ledger.py','test_a_share_evidence_*.py','test_a_share_remaining_blocker_register.py','test_a_share_next_reevaluation_prep_checklist.py','test_a_share_recovery_evidence*.py')
$tests = foreach ($pattern in $patterns) { Get-ChildItem tests -Filter $pattern }
$tests = $tests | Sort-Object FullName -Unique
python -m pytest @($tests.FullName)
```

The v0.8.18 release report must include:

- `full_pytest_run=false`
- `targeted_pytest_passed=true`
- `targeted_pytest_count=<actual>`
- `full_pytest_deferred_until=v0.9.0-or-big-version-closeout`
